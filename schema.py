from pydantic import BaseModel


class Predictions(BaseModel):
    id: int
    date: str
    prediction: str
    actual: float
    error: float
    model: str
    model_type: str
    data: str
    data_source: str


class Users(BaseModel):
    id: int
    username: str
    password: str
    email: str
    # predictions: list[Predictions] = []

    class Config:
        orm_mode = True  # This will allow the Pydantic model to accept ORM objects directly
