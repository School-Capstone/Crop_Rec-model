from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Predictions(Base):
    __tablename__ = 'predictions'
    id = Column(String(36), primary_key=True, index=True, default=str(uuid.uuid4))
    # user_id = Column(Integer, ForeignKey('users.id'))  # Add this line
    date = Column(DateTime, default=func.now())
    prediction = Column(String(100))
    actual = Column(Float)
    error = Column(Float)
    model = Column(String(100))
    model_type = Column(String(100))
    data = Column(String(20000))
    data_source = Column(String(100))
    # user = relationship("Users", back_populates="predictions")


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    password = Column(String(100))
    email = Column(String(100))
    # predictions = relationship("Predictions", backref="users")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

    def __str__(self):
        return f"<User(username={self.username}, email={self.email})>"
