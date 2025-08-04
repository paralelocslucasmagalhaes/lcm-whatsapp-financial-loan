from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

class RequestExtractOcr(BaseModel):
    user: str
    uri: str


class EnumEvent(str, Enum):
    UPLOAD = "upload"
    EXTRACT = "extract"
    STATUS = "status"

class RequestCheckStatus(BaseModel):
    user: str
    uri: str
    event: EnumEvent = EnumEvent.EXTRACT

# class ItemCreate(ItemBase):
#     pass

# class Item(ItemBase):
#     id: int

#     class Config:
#         orm_mode = True

# class UserBase(BaseModel):
#     username: str
#     email: str

# class UserCreate(UserBase):
#     password: str

# class User(UserBase):
#     id: int

#     class Config:
#         orm_mode = True


