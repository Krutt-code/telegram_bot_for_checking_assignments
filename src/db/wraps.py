from datetime import datetime
from functools import wraps

from src.db import database_logger


def log_db_performance(func):
    """
    Декоратор для логирования производительности запросов к БД.
    Применяется к асинхронным методам репозиториев.
    """
    _logger = database_logger.get_logger("db_performance")

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            elapsed_time = (
                datetime.now() - start_time
            ).total_seconds() * 1000  # в миллисекундах
            # Формируем имя метода: ИмяКласса.имя_метода если метод класса
            if args and hasattr(args[0], "__class__"):
                # Получаем имя функции безопасно
                func_name = getattr(func, "__name__", "unknown")
                method_name = f"{args[0].__class__.__name__}.{func_name}"
            else:
                method_name = getattr(func, "__name__", "unknown")

            _logger.info(
                f"DB Operation: {method_name} | Duration: {elapsed_time:.2f}ms | Args: {args[1:]} | Kwargs: {kwargs}"
            )
            return result
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            func_name = getattr(func, "__name__", "unknown")
            _logger.error(
                f"DB Error in {func_name} | Duration: {elapsed_time:.2f}ms | Error: {str(e)}",
                exc_info=True,
            )
            raise

    return wrapper
