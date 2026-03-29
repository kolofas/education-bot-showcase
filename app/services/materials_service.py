from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import logging

from app.database.models import Material
from app.database.schemas import MaterialData, MaterialOut, MaterialCreateRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


async def get_all_materials(user_id: int, db: AsyncSession) -> list[MaterialOut]:
    """Получение списка всех материалов пользователя"""
    try:
        query = select(Material).filter(Material.user_id == user_id)
        result = await db.execute(query)
        materials = result.scalars().all()

        if not materials:
            logging.info(f"Материалы для пользователя {user_id} не найдены")
            raise HTTPException(status_code=404, detail="Материалы не найдены")

        return [MaterialOut.model_validate(material) for material in materials]

    except Exception as e:
        logging.error(f"Ошибка получения материалов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def get_material_by_id(user_id: int, material_id: int, db: AsyncSession) -> MaterialOut:
    """Получение конкретного материала пользователя по его ID"""
    try:
        query = select(Material).filter(Material.user_id == user_id, Material.id == material_id)
        result = await db.execute(query)
        material = result.scalars().first()

        if not material:
            logging.info(f"Материал {material_id} для пользователя {user_id} не найден")
            raise HTTPException(status_code=404, detail="Материал не найден")

        return MaterialOut.model_validate(material)

    except Exception as e:
        logging.error(f"Ошибка получения материала {material_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def add_material_to_db(request: MaterialCreateRequest, db: AsyncSession) -> MaterialOut:
    """Добавление нового материала в базу данных"""
    try:
        new_material = Material(
            user_id=request.user_id,
            title=request.title,
            description=request.description,
            file_url=request.file_url
        )
        db.add(new_material)
        await db.commit()
        await db.refresh(new_material)

        logging.info(f"Материал '{request.title}' добавлен пользователем {request.user_id}")
        return MaterialOut.model_validate(new_material)

    except Exception as e:
        logging.error(f"Ошибка при добавлении материала: {str(e)}")
        await db.rollback()
        raise
