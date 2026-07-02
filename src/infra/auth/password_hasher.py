import bcrypt
from src.domain.users.value_objects import RawPassword
from src.domain.users.interfaces import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: RawPassword) -> str:
        return bcrypt.hashpw(str(password).encode(), bcrypt.gensalt()).decode()

    def verify(self, password: RawPassword, hashed: str) -> bool:
        return bcrypt.checkpw(str(password).encode(), hashed.encode())
