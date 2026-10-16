from enum import Enum
from fastapi import Depends

from passlib.context import CryptContext





pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")





class Role(str, Enum):


    faculty = "faculty"


    admin = "admin"


    student = "student"





def verify_password(plain: str, hashed: str) -> bool:


    return pwd_context.verify(plain, hashed)





def get_password_hash(password: str) -> str:


    return pwd_context.hash(password)



