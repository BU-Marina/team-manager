from passlib.context import CryptContext

from src.domain.users.value_objects import RawPassword
from src.domain.users.interfaces import PasswordHasher

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: RawPassword) -> str:
        return pwd_context.hash(str(password))

    def verify(self, password: RawPassword, hashed: str) -> bool:
        return pwd_context.verify(str(password), hashed)
