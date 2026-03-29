import asyncio
import logging

from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.configurations.config import BOT_TOKEN
from app.database.database import init_db, engine, get_db
from app.utils.jwt_utils import verify_token

from app.bot.start import router as start_router
from app.bot.authentication import router as auth_router
from app.bot.bonuses import router as bonuses_router
from app.bot.materials import router as material_router
from app.bot.menu import router as menu_router
from app.bot.profile import router as profile_router
from app.bot.registration import router as registration_router
from app.bot.school_services import router as school_services_router
from app.bot.social_network import router as social_networks_router
from app.bot.fallback import router as fallback_router

from app.database.schemas import (
    UserRegistrationRequest,
    UserCheckResponse,
    UserLoginRequest,
    UserLoginResponse,
    UpdateProfileRequest,
    MaterialData,
    MaterialCreateRequest,
    SchoolServiceCreateRequest,
    SchoolServiceData,
    BonusOut,
    BonusCreateRequest,
    TokenResponse,
    AuthorizedResponse,
    MessageResponse,
    TokenResetResponse,
    SocialNetworkOut,
    SocialNetworkCreateRequest, MaterialOut, SchoolServiceOut)

from app.services.authentication_service import (
    authenticate_user
)
from app.services.bonuses_service import (
    get_all_bonuses,
    get_bonus_by_id,
    add_bonus_to_db
)
from app.services.materials_service import (
    get_all_materials,
    get_material_by_id,
    add_material_to_db
)
from app.services.profile_service import (
    get_user_profile,
    get_user_token,
    update_user_profile,
    logout_user,
    reset_user_token
)
from app.services.registration_service import (
    register_user_in_database,
    is_user_registered
)
from app.services.school_services_service import (
    get_all_services,
    get_service_by_id,
    add_service_to_db
)
from app.services.social_network_service import (
    get_all_social_networks,
    get_social_network_by_id,
    add_social_network_to_db
)


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(registration_router)
dp.include_router(menu_router)
dp.include_router(auth_router)
dp.include_router(profile_router)
dp.include_router(material_router)
dp.include_router(school_services_router)
dp.include_router(bonuses_router)
dp.include_router(social_networks_router)
dp.include_router(fallback_router) # ← этот роутер должен быть последним
# dp.include_router(progress_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер для старта и остановки сервера"""
    try:
        await init_db()

        # Проверка списка таблиц в БД
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                    SELECT table_name FROM information_schema.tables WHERE table_schema='public'
                """))
            tables = result.fetchall()
            logging.info(f"Таблицы в базе данных: {tables}")

        await bot.set_my_commands([
            BotCommand(command='/start', description='Начнем работу!'),
            BotCommand(command='/menu', description='Вызов главного меню'),
            BotCommand(command='/info', description='Об этом боте'),
        ])

        # Запуск бота
        polling_task = asyncio.create_task(dp.start_polling(bot))
        yield # <-- Ожидание завершения работы приложения


    finally:
        logging.info("Останавливаем бота...")
        polling_task.cancel()
        try:
            await polling_task  # Дождаться завершения таски
        except asyncio.CancelledError:
            logging.info("Polling task was cancelled")
        await bot.session.close()
        logging.info("Бот остановлен")

app = FastAPI(lifespan=lifespan)

@app.post("/register/", response_model=TokenResponse)
async def register_user(user: UserRegistrationRequest, db: AsyncSession = Depends(get_db)):
    logging.info(f"Полученные данные пользователя: {user}")
    return await register_user_in_database(user, db)

@app.get("/check_user/{user_id}", response_model=UserCheckResponse)
async def check_user(user_id: int, db: AsyncSession = Depends(get_db)):
    logging.info(f"Проверка пользователя с ID: {user_id}")
    return await is_user_registered(user_id, db)

@app.post("/authenticate/", response_model=UserLoginResponse)
async def auth_user(user: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Авторизация пользователя и выдача токена"""
    logging.info(f"Попытка входа для user_id: {user.user_id}")

    token_model = await authenticate_user(user, db)

    if not token_model:
        logging.warning(f"Ошибка авторизации для user_id: {user.user_id}")
        return JSONResponse(status_code=401, content={"error": "Неверный логин или пароль"})

    return token_model

@app.get("/check-auth/{user_id}", response_model=AuthorizedResponse)
async def check_user_auth(user_id: int, db: AsyncSession =Depends(get_db)):
    """Проверка авторизован ли пользователь и действителен ли токен"""
    try:
        token = await get_user_token(user_id, db)
        verify_token(token, user_id)
        return AuthorizedResponse(authorized=True)
    except HTTPException as e:
        logging.warning(f"Пользователь {user_id} не авторизован: {e.detail}")
        return AuthorizedResponse(authorized=False)

@app.get("/token/{user_id}", response_model=TokenResponse)
async def get_token(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получает токен пользователя из базы данных"""
    return TokenResponse(access_token=await get_user_token(user_id, db))

@app.get("/profile/{user_id}")
async def get_profile(user_id: int,
                      db: AsyncSession = Depends(get_db),
                      authorization: str = Header(None)
                      ):
    verify_token(authorization, user_id)
    return await get_user_profile(user_id, db)

@app.put("/profile/{user_id}")
async def update_profile(user_id: int,
                         request: UpdateProfileRequest,
                         db: AsyncSession = Depends(get_db),
                         authorization: str = Header(None)
                         ):
    verify_token(authorization, user_id)
    return await update_user_profile(user_id, request.username, db)

@app.post("/logout/{user_id}", response_model=MessageResponse)
async def logout(user_id: int,
                 db: AsyncSession = Depends(get_db),
                 authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await logout_user(user_id, db)

@app.post("/reset-token/{user_id}", response_model=TokenResetResponse)
async def reset_token(user_id: int,
                      db: AsyncSession = Depends(get_db),
                      authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await reset_user_token(user_id, db)

@app.get("/materials/list")
async def get_materials(user_id: int,
                        db: AsyncSession = Depends(get_db),
                        authorization: str = Header(None)):
    """Эндпоинт для получения списка всех материалов"""
    verify_token(authorization, user_id)
    return await get_all_materials(user_id, db)

@app.get("/materials/{material_id}")
async def get_material(material_id: int,
                       user_id: int,
                       db: AsyncSession = Depends(get_db),
                       authorization: str = Header(None)):
    """Эндпоинт для получения конкретного материала"""
    verify_token(authorization, user_id)
    return await get_material_by_id(user_id, material_id, db)

@app.post("/materials/add", status_code=201, response_model=MaterialOut)
async def add_material(request: MaterialCreateRequest,
                       authorization: str = Header(None),
                       db: AsyncSession = Depends(get_db)) -> MaterialOut:
    """Эндпоинт для добавления нового материала"""
    verify_token(authorization, request.user_id)

    try:
        return await add_material_to_db(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@app.get("/school_services/list")
async def get_services_list(user_id: int,
                            db: AsyncSession = Depends(get_db),
                            authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await get_all_services(user_id, db)

@app.get("/school_services/{service_id}")
async def get_service(service_id: int,
                      user_id: int,
                      db: AsyncSession = Depends(get_db),
                      authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await get_service_by_id(user_id, service_id, db)

@app.post("/school_services/add", status_code=201, response_model=SchoolServiceOut)
async def add_service(
        request: SchoolServiceCreateRequest,
        db: AsyncSession = Depends(get_db),
        authorization: str = Header(None)
):
    verify_token(authorization, request.user_id)
    return await add_service_to_db(request, db)

@app.get("/bonuses/list", response_model=list[BonusOut])
async def get_bonuses_list(user_id: int,
                           db: AsyncSession = Depends(get_db),
                           authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await get_all_bonuses(user_id, db)

@app.get("/bonuses/{bonus_id}", response_model=BonusOut)
async def get_bonus(bonus_id: int,
                    user_id: int,
                    db: AsyncSession = Depends(get_db),
                    authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await get_bonus_by_id(user_id, bonus_id, db)

@app.post("/bonuses/add", response_model=BonusOut, status_code=201)
async def add_bonus(request: BonusCreateRequest,
                    db: AsyncSession = Depends(get_db),
                    authorization: str = Header(None)):
    verify_token(authorization, request.user_id)
    return await add_bonus_to_db(request, db)

@app.get("/social_networks/list", response_model=list[SocialNetworkOut])
async def get_social_networks(user_id: int,
                              db: AsyncSession = Depends(get_db),
                              authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await get_all_social_networks(user_id, db)

@app.get("/social_networks/{social_id}", response_model=SocialNetworkOut)
async def get_social_network_by_id_api(social_id: int,
                                   user_id: int,
                                   db: AsyncSession = Depends(get_db),
                                   authorization: str = Header(None)):
    verify_token(authorization, user_id)
    return await get_social_network_by_id(user_id, social_id, db)

@app.post("/social_networks/add", status_code=201, response_model=SocialNetworkOut)
async def add_social_network(request: SocialNetworkCreateRequest,
                             db: AsyncSession = Depends(get_db),
                             authorization: str = Header(None)):
    verify_token(authorization, request.user_id)
    return await add_social_network_to_db(request, db)

@app.get('/')
async def home():
    return {"message": "Сервер работает, бота запущен"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
