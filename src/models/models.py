from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from sqlalchemy_utils import IPAddressType

from src.db.db import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(1000), unique=True, nullable=False)
    password = Column(String(1000), nullable=False)
    created_at = Column(
        DateTime, index=True, default=func.now(), nullable=False
    )

    short_url_info = relationship(
        "ShortedURLInfo", back_populates="user", cascade="all, delete"
    )

    def __repr__(self):
        return f"User(id={self.id}, {self.username})"


class ShortedURL(Base):
    __tablename__ = "shorted_url"
    id = Column(Integer, primary_key=True)
    value = Column(String(1000), unique=True, nullable=False)
    original = Column(String(1000), unique=True, nullable=False)
    created_at = Column(
        DateTime, index=True, default=func.now(), nullable=False
    )
    deleted = Column(Boolean, default=False)

    uses = relationship(
        "ShortedURLInfo", back_populates="url", cascade="all, delete"
    )

    def __repr__(self):
        return f"ShortedURL({self.value}, original={self.original})"


class ShortedURLInfo(Base):
    __tablename__ = "shorted_url_info"
    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime, index=True, default=func.now(), nullable=False
    )
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    user_agent = Column(String(1000), nullable=False)
    url_id = Column(ForeignKey("shorted_url.id"), nullable=False)
    user_id = Column(ForeignKey("user.id"), nullable=True)

    url = relationship("ShortedURL", back_populates="uses")
    user = relationship("User", back_populates="short_url_info")

    def __repr__(self):
        return (
            f"ShortedURLInfo(peer={self.host}:{self.port},"
            f" url={self.url_id}, user={self.user_id})"
        )


class BlacklistedClient(Base):
    __tablename__ = "blacklisted_client"
    id = Column(Integer, primary_key=True)
    host = Column(IPAddressType)
    until = Column(DateTime, index=True, default=None, nullable=True)

    def __repr__(self):
        return f"BlacklistedClient({self.host})"