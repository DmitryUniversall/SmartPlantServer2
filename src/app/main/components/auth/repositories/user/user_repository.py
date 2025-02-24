from src.app.bases.repositories import ObservableRepository
from src.app.main.components.auth.entities.user.model import UserModel
from src.app.main.db import AsyncDatabaseManagerST
from src.core.utils.singleton import ABCSingletonMeta


class UserRepositoryST(ObservableRepository[UserModel, int], metaclass=ABCSingletonMeta):
    __model_cls__: type[UserModel] = UserModel
    __db_manager__: AsyncDatabaseManagerST = AsyncDatabaseManagerST()
