import hashlib

from src.app.bases.resources import ObservableResource
from src.app.main.db import AsyncDatabaseManagerST
from src.core.utils.singleton import ABCSingletonMeta
from .model import UserModel


class UserResourceST(ObservableResource[UserModel, int], metaclass=ABCSingletonMeta):
    __model_cls__: type[UserModel] = UserModel
    __db_manager__: AsyncDatabaseManagerST = AsyncDatabaseManagerST()

    def hash_password(self, password: str, encoding: str = "utf-8") -> str:
        return hashlib.sha256(password.encode(encoding=encoding)).hexdigest()

    async def get_by_credentials(self, username: str, password: str, **fields) -> UserModel:
        password = self.hash_password(password)

        if (user := await self.get_one_by(username=username, password=password, **fields)) is not None:
            return user

        raise UserModel.DoesNotExist("User not found")

    async def create_user(self, username: str, password: str, **fields) -> UserModel:
        user = UserModel(username=username, password=self.hash_password(password), **fields)

        await self.create(user)
        return user

    async def get_by_username(self, username: str, **fields) -> UserModel:
        if (user := await self.get_one_by(username=username, **fields)) is not None:
            return user
        raise UserModel.DoesNotExist("User not found")
