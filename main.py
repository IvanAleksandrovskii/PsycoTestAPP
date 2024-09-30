# main.py

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncio

from fastapi.responses import ORJSONResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from sqladmin import Admin

from core.admin import async_sqladmin_db_helper, sqladmin_authentication_backend
from core.models import db_helper
from core.admin.models import setup_admin

from core import settings, logger

from bot_main import main as start_bot



def run_async(func):
    loop = asyncio.get_event_loop()
    return lambda: loop.create_task(func())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # not used: ignore
    # Startup
    logger.info("Starting up the FastAPI application...")

    # Start the bot in a separate task
    bot_task = asyncio.create_task(start_bot())

    yield

    # Shutdown
    logger.info("Shutting down the FastAPI application...")

    await db_helper.dispose()
    await async_sqladmin_db_helper.dispose()

    # Cancel the bot task
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        logger.info("Bot task cancelled successfully")


main_app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

# SQLAdmin
admin = Admin(main_app, engine=async_sqladmin_db_helper.engine, authentication_backend=sqladmin_authentication_backend)

# Register admin views
setup_admin(admin)


# Favicon.ico errors silenced
@main_app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# Global exception handler
@main_app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        if request.url.path == "/favicon.ico":
            return Response(status_code=204)

        if isinstance(exc, ValueError) and "badly formed hexadecimal UUID string" in str(exc):
            return Response(status_code=204)

        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )


class NoFaviconFilter(logging.Filter):
    def filter(self, record):
        return not any(x in record.getMessage() for x in ['favicon.ico', 'apple-touch-icon'])


logging.getLogger("uvicorn.access").addFilter(NoFaviconFilter())

# CORS
main_app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == '__main__':
    uvicorn.run("main:main_app",
                host=settings.run.host,
                port=settings.run.port,
                reload=settings.run.debug,
    )
