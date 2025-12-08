from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=True)
