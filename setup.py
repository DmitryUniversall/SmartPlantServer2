import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI

from src.app.bases.db import BaseModel
from src.app.main.db import AsyncDatabaseManagerST
from src.app.main.routes import project_router
from src.core.loggers import LoggerBuilder
from src.core.project_state import ProjectState
from src.core.state import project_settings
from src.core.utils.errors import supress_exception
from src.app.main.exceptions.handlers import __handlers__


def setup_loggers() -> logging.Logger:
    if project_settings.STATE == ProjectState.PRODUCTION:
        with supress_exception(FileNotFoundError):
            os.remove(project_settings.LATEST_LOG_FILE_PATH)

        return (
            LoggerBuilder('src', logging.DEBUG)
            .enable_console(
                level=project_settings.CONSOLE_LOG_LEVEL
            )
            .add_file(
                project_settings.APPLICATION_LOG_FILE_PATH,
                handler_cls=RotatingFileHandler,
                maxBytes=project_settings.APPLICATION_LOG_MAX_FILE_SIZE,
                backupCount=project_settings.APPLICATION_LOG_BACKUP_COUNT,
                level=project_settings.FILE_LOG_LEVEL
            )
            .add_file(
                project_settings.LATEST_LOG_FILE_PATH,
                handler_cls=RotatingFileHandler,
                maxBytes=project_settings.LATEST_LOG_MAX_FILE_SIZE,
                backupCount=project_settings.LATEST_LOG_BACKUP_COUNT,
                level=project_settings.FILE_LOG_LEVEL
            )
            .get()
        )

    return (
        LoggerBuilder('src', logging.DEBUG)
        .enable_console(level=logging.DEBUG)
        .get()
    )


async def setup_routes(app: FastAPI) -> None:
    app.include_router(project_router, prefix="/api")


async def setup_error_handlers(app: FastAPI) -> None:
    for handler in __handlers__:
        app.add_exception_handler(handler.__exception_cls__, handler)


async def setup_database() -> None:
    db_manager = await AsyncDatabaseManagerST()  # await runs initialization
    project_settings.DB_MANAGER = db_manager

    await setup_database_models(db_manager)


async def setup_database_models(db_manager: 'AsyncDatabaseManagerST') -> None:
    async with db_manager.engine.begin() as conn:
        # if project_settings.STATE != ProjectState.PRODUCTION:
        #     await conn.run_sync(BaseModel.metadata.drop_all)

        await conn.run_sync(BaseModel.metadata.create_all)
