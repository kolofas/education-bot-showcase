from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import logging

from app.database.schemas import (
    SchoolServiceData,
    SchoolServiceOut,
    SchoolServiceCreateRequest
)
from app.database.models import SchoolService


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


async def get_all_services(user_id: int, db: AsyncSession) -> list[SchoolServiceOut]:
    """Получение списка всех товаров и услуг"""
    try:
        query = select(SchoolService).filter(SchoolService.user_id == user_id)
        result = await db.execute(query)
        school_services = result.scalars().all()

        if not school_services:
            logging.info(f"Услуги школы для пользователя {user_id} не найдены")
            raise HTTPException(status_code=404, detail="Услуги школы не найдены")

        return [SchoolServiceOut.model_validate(school_service) for school_service in school_services]

    except Exception as e:
        logging.error(f"Ошибка получения услуг школы: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def get_service_by_id(user_id: int, service_id: int, db: AsyncSession) -> SchoolServiceOut:
    """Получение конкретной услуги по ее ID"""
    try:
        query = select(SchoolService).filter(SchoolService.user_id == user_id, SchoolService.id == service_id)
        result = await db.execute(query)
        school_service = result.scalars().first()

        if not school_service:
            logging.info(f'Услуга {service_id} для пользователя {user_id} не найдена')
            raise HTTPException(status_code=404, detail="Услуга не найдена")

        return SchoolServiceOut.model_validate(school_service)

    except Exception as e:
        logging.error(f"Ошибка получения услуги {service_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def add_service_to_db(request: SchoolServiceCreateRequest, db: AsyncSession) -> SchoolServiceOut:
    """Добавление новой услуги/товара в базу данных"""
    try:
        new_school_service = SchoolService(
            user_id=request.user_id,
            title=request.title,
            description=request.description,
            price=request.price
        )
        db.add(new_school_service)
        await db.commit()
        await db.refresh(new_school_service)

        logging.info(f"Услуга/товар '{request.title}' добавлен пользователем {request.user_id}")

        return SchoolServiceOut.model_validate(new_school_service)

    except Exception as e:
        logging.error(f"Ошибка при добавлении товара/услуги: {str(e)}")
        await db.rollback()
        raise
