from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
from fastapi import HTTPException
from app.database.schemas import BonusOut, BonusCreateRequest
from app.database.models import Bonus


# Получить все активные бонусы для пользователя
async def get_all_bonuses(user_id: int, db: AsyncSession) -> list[BonusOut]:
    try:
        query = select(Bonus).filter(Bonus.user_id == user_id, Bonus.is_active == True)
        result = await db.execute(query)
        bonuses = result.scalars().all()

        if not bonuses:
            logging.info(f"Бонусы для пользователя {user_id} не найдены")
            raise HTTPException(status_code=404, detail="Бонусы не найдены")

        return [BonusOut.model_validate(bonus) for bonus in bonuses]

    except Exception as e:
        logging.error(f"Ошибка получения бонусов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


# Получить бонус по ID
async def get_bonus_by_id(user_id: int, bonus_id: int, db: AsyncSession) -> BonusOut:
    try:
        query = select(Bonus).filter(Bonus.user_id == user_id, Bonus.id == bonus_id)
        result = await db.execute(query)
        bonus = result.scalars().first()

        if not bonus:
            logging.info(f"Бонус {bonus_id} не найден для пользователя {user_id}")
            raise HTTPException(status_code=404, detail="Бонус не найден")

        return BonusOut.model_validate(bonus)

    except Exception as e:
        logging.error(f"Ошибка получения бонуса {bonus_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


# Добавить бонус в БД
async def add_bonus_to_db(request: BonusCreateRequest, db: AsyncSession) -> BonusOut:
    try:
        new_bonus = Bonus(
            title=request.title,
            description=request.description,
            action_text=request.action_text,
            user_id=request.user_id,
            is_active=request.is_active
        )
        db.add(new_bonus)
        await db.commit()
        await db.refresh(new_bonus)

        logging.info(f"Бонус '{request.title}' добавлен пользователем {request.user_id}")
        return BonusOut.model_validate(new_bonus)

    except Exception as e:
        logging.error(f"Ошибка при добавлении бонуса: {str(e)}")
        await db.rollback()
        raise