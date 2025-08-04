from pydantic import BaseModel
from typing import List, Optional

class RequestMessage(BaseModel):
    From: str = None
    body: str = None
    to: str = None

class RequestChat(BaseModel):
    session_id: str = None
    message: str = None    


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


