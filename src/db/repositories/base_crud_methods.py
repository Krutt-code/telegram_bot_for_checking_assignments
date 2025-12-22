from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.session import with_session
from src.db.wraps import log_db_performance

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class BaseCRUDMethods(Generic[ModelType, SchemaType, CreateSchemaType]):
    """
    Базовый класс для CRUD-операций.

    Для использования:
    - Наследуемся от класса.
    - Определяем class-атрибуты:
        model: SQLAlchemy-модель
        schema: Pydantic-схема
        id_column: имя колонки, по которой ищем / обновляем / удаляем (по умолчанию "id").
    """

    model: Type[ModelType]
    schema: Type[SchemaType]
    create_schema: Type[CreateSchemaType]
    id_column: str = "id"
    base_relationships: list[str] = []

    @classmethod
    def get_base_relationships(cls) -> list[str]:
        """
        Получить список базовых relationships.
        """
        return cls.base_relationships

    @classmethod
    def _add_relationships_to_query(
        cls, query: Select, relationships: Optional[list[str]] = None
    ) -> Select:
        """
        Добавить relationship к запросу.
        """
        relationships = set(cls.base_relationships + (relationships or []))

        def _joinedload_option(path: str):
            """
            Создание дополнительного запроса для relationship.
            """
            parts = [p for p in (path or "").split(".") if p]
            if not parts:
                return None

            if not hasattr(cls.model, parts[0]):
                return None

            current_attr = getattr(cls.model, parts[0])
            opt = joinedload(current_attr)

            for part in parts[1:]:
                # Determine target class for the current relationship
                try:
                    target_cls = current_attr.property.mapper.class_
                except Exception:
                    return opt

                if not hasattr(target_cls, part):
                    return opt

                next_attr = getattr(target_cls, part)
                opt = opt.joinedload(next_attr)
                current_attr = next_attr

            return opt

        for relationship_path in relationships:
            opt = _joinedload_option(relationship_path)
            if opt is not None:
                query = query.options(opt)
        return query

    @classmethod
    def _apply_where(cls, query: Select, where: dict) -> Select:
        """
        Применить where-условия к запросу.

        Поддерживает два формата ключей:
        - str: имя поля модели, например {"group_id": 1}
        - SQLAlchemy-колонка: например {StudentsModel.group_id: 1}
        """
        for key, value in (where or {}).items():
            if isinstance(key, str):
                if not hasattr(cls.model, key):
                    raise AttributeError(
                        f"{cls.model.__name__} has no column/attr '{key}'"
                    )
                query = query.where(getattr(cls.model, key) == value)
            else:
                # предполагаем, что это SQLAlchemy ColumnElement
                query = query.where(key == value)
        return query

    @classmethod
    @log_db_performance
    @with_session
    async def get_by_id(
        cls,
        id_value: int,
        load_relationships: Optional[list[str]] = None,
        session: AsyncSession = None,
    ) -> Optional[SchemaType]:
        """
        Получить одну запись по значению ID-колонки (по умолчанию user_id).

        Args:
            id_value: Значение ID для поиска
            session: Сессия БД (передается автоматически декоратором)
            load_relationships: Список имен relationships для eager loading
                               Например: ['user', 'group'] для StudentsModel

        Returns:
            SchemaType или None если запись не найдена
        """
        column = getattr(cls.model, cls.id_column)
        query = select(cls.model).filter(column == id_value)

        query = cls._add_relationships_to_query(query, load_relationships)
        res = await session.execute(query)
        model_instance = res.unique().scalars().first()
        if model_instance:
            return cls.schema.model_validate(model_instance)
        return None

    @classmethod
    @log_db_performance
    @with_session
    async def get_all_where(
        cls,
        where: dict,
        load_relationships: Optional[list[str]] = None,
        session: AsyncSession = None,
    ) -> list[SchemaType]:
        """
        Получить все записи по условию с загруженными relationships.

        Args:
            where: Словарь условий для фильтрации
            load_relationships: Список имен relationships для eager loading
            session: Сессия БД (передается автоматически декоратором)

        Returns:
            Список схем
        """
        query = select(cls.model)
        query = cls._apply_where(query, where)

        query = cls._add_relationships_to_query(query, load_relationships)

        res = await session.execute(query)
        model_instances = res.unique().scalars().all()
        if model_instances:
            return [cls.schema.model_validate(instance) for instance in model_instances]
        return []

    @classmethod
    @log_db_performance
    @with_session
    async def create(
        cls,
        schema: CreateSchemaType,
        session: AsyncSession = None,
    ) -> int:
        """
        Создать запись на основе Pydantic-схемы.

        Returns:
            int: Значение ID-колонки созданной записи.
        """
        model_instance = cls.model(**schema.model_dump())
        session.add(model_instance)
        await session.flush()
        return getattr(model_instance, cls.id_column)

    @classmethod
    @log_db_performance
    @with_session
    async def update(
        cls,
        where: dict,
        schema_for_update: SchemaType,
        session: AsyncSession = None,
    ) -> int:
        """
        Обновить запись по условию.

        Returns:
            int: Количество обновленных записей.
        """
        data_for_update = schema_for_update.model_dump(exclude_unset=True)
        query = update(cls.model)
        for key, value in (where or {}).items():
            if isinstance(key, str):
                query = query.where(getattr(cls.model, key) == value)
            else:
                query = query.where(key == value)
        res = await session.execute(query.values(**data_for_update))
        return res.rowcount

    @classmethod
    @log_db_performance
    @with_session
    async def update_values(
        cls,
        where: dict,
        values: dict,
        session: AsyncSession = None,
    ) -> int:
        """
        Обновить запись(и) по условию значениями из обычного dict.

        Returns:
            int: Количество обновленных записей.
        """
        query = update(cls.model)
        for key, value in (where or {}).items():
            if isinstance(key, str):
                query = query.where(getattr(cls.model, key) == value)
            else:
                query = query.where(key == value)
        res = await session.execute(query.values(**(values or {})))
        return res.rowcount

    @classmethod
    @log_db_performance
    @with_session
    async def update_values_by_id(
        cls,
        id_value: int,
        values: dict,
        session: AsyncSession = None,
    ) -> bool:
        """
        Обновить запись по значению ID-колонки значениями из dict.
        """
        res = await cls.update_values(
            where={cls.id_column: id_value},
            values=values,
            session=session,
        )
        return res > 0

    @classmethod
    @log_db_performance
    @with_session
    async def update_by_id(
        cls,
        id_value: int,
        schema_for_update: SchemaType,
        session: AsyncSession = None,
    ) -> bool:
        """
        Обновить запись по значению ID-колонки.
        """
        res = await cls.update(
            where={cls.id_column: id_value},
            schema_for_update=schema_for_update,
            session=session,
        )
        return res > 0

    @classmethod
    @log_db_performance
    @with_session
    async def delete(
        cls,
        where: dict,
        session: AsyncSession = None,
    ) -> int:
        """
        Удалить запись по условию.

        Returns:
            int: Количество удаленных записей.
        """
        query = delete(cls.model)
        for key, value in (where or {}).items():
            if isinstance(key, str):
                query = query.where(getattr(cls.model, key) == value)
            else:
                query = query.where(key == value)
        res = await session.execute(query)
        return res.rowcount

    @classmethod
    @log_db_performance
    @with_session
    async def delete_by_id(
        cls,
        id_value: int,
        session: AsyncSession = None,
    ) -> bool:
        """
        Удалить запись по значению ID-колонки.
        """
        return await cls.delete(where={cls.id_column: id_value}, session=session) > 0
