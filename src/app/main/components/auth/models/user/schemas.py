from datetime import datetime

from src.app.bases.db import BaseSchema


# As User class is generated dynamically during runtime, it's bad for type checking.
# I don't know if it is a good solution, so I'll just comment it
# User: Type[BaseSchema] = UserModel.as_pydantic_scheme()


class UserPublic(BaseSchema):  # For public usage. Can be shown to other users
    id: int
    username: str
    created_at: datetime


class UserPrivate(UserPublic):  # For private usage. Can only be shown to user-owner
    pass


class UserInternal(UserPrivate):  # For internal usage. Must not be used outside application
    pass
