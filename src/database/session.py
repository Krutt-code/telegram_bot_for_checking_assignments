from contextlib import asynccontextmanager
from datetime import datetime
from functools import wraps

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.settings import settings
from src.database import database_logger

# 1. Создаем асинхронный "движок" для подключения к базе данных.
# Оптимизированные настройки для MySQL 5.7
async_engine = create_async_engine(
    settings.actual_database_url,
    echo=False,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=600,  # Переподключение соединений каждые 10 минут (более агрессивно)
    pool_size=(settings.db_pool_size or 5),  # Увеличиваем размер пула
    max_overflow=(
        settings.db_max_overflow or 10
    ),  # Разрешаем больше временных соединений
    pool_timeout=(settings.db_pool_timeout or 30),
    # # Важные настройки для MySQL 5.7
    # connect_args={
    #     "ssl": (
    #         {"ssl_verify_cert": False}
    #         if settings.actual_database_url.startswith("mysql")
    #         else {}
    #     ),
    # },
)

# 2. Создаем "фабрику сессий".
# Этот объект будет создавать новые, изолированные сессии по запросу.
# expire_on_commit=False важно для асинхронного кода, чтобы объекты
# оставались доступными после коммита.
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
session_logger = database_logger.get_logger("session")


@event.listens_for(async_engine.sync_engine, "connect", insert=True)
def set_wait_timeout(dbapi_connection, connection_record):
    """
    Устанавливает оптимизированные параметры MySQL при подключении.
    Эти настройки помогают с долгими соединениями и распределением нагрузки.
    """
    cursor = dbapi_connection.cursor()
    try:
        # Увеличиваем wait_timeout для предотвращения обрывов соединения
        cursor.execute("SET SESSION wait_timeout = 1800")  # 30 минут
        cursor.execute("SET SESSION innodb_lock_wait_timeout = 120")  # 2 минуты
        # Отключаем автокоммит для транзакций
        cursor.execute("SET autocommit = 0")
        # Установка уровня изоляции для уменьшения блокировок
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
    except Exception as e:
        session_logger.error(f"Error setting MySQL session parameters: {e}")
    finally:
        cursor.close()


@asynccontextmanager
async def get_db_session():
    """
    Контекстный менеджер для получения сессии БД с отслеживанием производительности.
    """
    start_time = datetime.now()
    session = async_session_factory()
    try:
        yield session
        await session.commit()
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        session_logger.info(f"DB Session duration: {elapsed:.2f}ms (committed)")
    except Exception as e:
        await session.rollback()
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        session_logger.error(f"DB Session error: {elapsed:.2f}ms | {str(e)}")
        raise
    finally:
        await session.close()


def with_session(func):
    """
    Декоратор для асинхронных функций, который предоставляет
    изолированную сессию базы данных.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Проверяем, была ли сессия уже передана как аргумент.
        # Это позволяет вкладывать вызовы функций с декоратором в одну транзакцию.
        if "session" in kwargs and kwargs["session"] is not None:
            return await func(*args, **kwargs)

        # Если сессии нет, создаем новую, используя нашу фабрику.
        async with async_session_factory() as session:
            try:
                # Передаем новую сессию в декорируемую функцию.
                kwargs["session"] = session
                result = await func(*args, **kwargs)
                # Коммитим транзакцию, если функция выполнилась успешно.
                await session.commit()
                return result
            except Exception:
                # В случае любой ошибки откатываем транзакцию.
                await session.rollback()
                # И пробрасываем исключение дальше.
                raise

    return wrapper
