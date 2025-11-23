from sqlalchemy import Column, Integer, String,Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    watchlist = relationship("WatchlistItem", back_populates="user")


class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    coin_name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    price = Column(Float, nullable=True)
    change = Column(Float, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="watchlist")
