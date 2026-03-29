from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
from fastapi import HTTPException
from app.database.schemas import (
    SocialNetworkOut,
    SocialNetworkCreateRequest
)
from app.database.models import SocialNetwork


async def get_all_social_networks(user_id: int, db: AsyncSession) -> list[SocialNetworkOut]:
    """Получение всех социальных сетей"""
    try:
        query = select(SocialNetwork).filter(SocialNetwork.user_id == user_id)
        result = await db.execute(query)
        social_networks = result.scalars().all()

        if not social_networks:
            logging.info(f"Социальные сети для пользователя {user_id} не найдены")
            raise HTTPException(status_code=404, detail="Социальные сети не найдены")

        return [SocialNetworkOut.model_validate(social_network) for social_network in social_networks]

    except Exception as e:
        logging.error(f"Ошибка получения социальных сетей: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


async def get_social_network_by_id(user_id: int, social_network_id: int, db: AsyncSession) -> SocialNetworkOut:
    """Получение конкретной социальной сети"""
    try:
        query = select(SocialNetwork).filter(SocialNetwork.user_id == user_id, SocialNetwork.id == social_network_id)
        result = await db.execute(query)
        social_network = result.scalars().first()

        if not social_network:
            logging.info(f"Социальная сеть {social_network_id} не найдена для пользователя {user_id}")
            raise HTTPException(status_code=404, detail="Ошибка сервера")

        return SocialNetworkOut.model_validate(social_network)

    except Exception as e:
        logging.error(f"Ошибка получения бонуса {social_network_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


async def add_social_network_to_db(request: SocialNetworkCreateRequest, db: AsyncSession) -> SocialNetworkOut:
    """Добавление новой социальной сети"""
    try:
        new_social_network = SocialNetwork(
            user_id=request.user_id,
            platform=request.platform,
            url=request.url,
            phone=request.phone
        )

        db.add(new_social_network)
        await db.commit()
        await db.refresh(new_social_network)

        logging.info(f"Социальная сеть '{request.platform}' добавлена пользователем {request.user_id}")
        return SocialNetworkOut.model_validate(new_social_network)

    except Exception as e:
        logging.error(f"Ошибка при добавлении социальной сети: {str(e)}")
        await db.rollback()
        raise

