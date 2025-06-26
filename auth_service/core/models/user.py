from sqlalchemy.orm import Mapped
from core.models import (
    Base,
    str_uniq,
    uuid_pk,
)



class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid_pk]
    phone_number: Mapped[str_uniq]
    username: Mapped[str_uniq]
    email: Mapped[str_uniq]
    password: Mapped[bytes]

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
