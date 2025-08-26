<<<<<<< HEAD
from pydantic import BaseModel


class RegisterBody(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


=======
from pydantic import BaseModel


class RegisterBody(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


>>>>>>> 1b483347e328bcc78652b1a0b4ad12102aaaee5c
