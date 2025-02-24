import hashlib

from src.app.main.components.auth.entities.user import UserModel, UserInternal
from src.app.main.components.auth.repositories.user.user_repository import UserRepositoryST
from src.core.utils.singleton import SingletonMeta


class UserServiceST(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._user_repository = UserRepositoryST()

    def hash_password(self, password: str, encoding: str = "utf-8") -> str:
        return hashlib.sha256(password.encode(encoding=encoding)).hexdigest()

    async def create_user(self, username: str, password: str, **fields) -> UserInternal:
        user_model = UserModel(username=username, password=self.hash_password(password), **fields)
        await self._user_repository.create(user_model)
        return user_model.to_schema(UserInternal)

    async def get_by_username(self, username: str, **fields) -> UserInternal:
        user_model = await self._user_repository.get_one_by_strict(username=username, **fields)
        return user_model.to_schema(UserInternal)

    async def get_user_by_id(self, user_id: int) -> UserInternal:
        user_model = await self._user_repository.get_by_pk_strict(user_id)
        return user_model.to_schema(UserInternal)

    async def get_by_auth_credentials(self, username: str, password_raw: str, **fields) -> UserInternal:
        password_hash = self.hash_password(password_raw)
        user_model = await self._user_repository.get_one_by_strict(username=username, password=password_hash, **fields)
        return user_model.to_schema(UserInternal)
