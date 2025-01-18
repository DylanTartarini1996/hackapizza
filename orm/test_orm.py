from typing import Optional, List
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import json

class Base(DeclarativeBase):
    pass

class Dishes(Base):
    __tablename__ = "dishes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"))
    ingredients: Mapped[List["Ingredient"]] = relationship()
    techniques: Mapped[List["Technique"]] = relationship()

class Restaurant(Base):
    __tablename__ = "restaurant"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    chef: Mapped[str] = mapped_column(String(30))
    location: Mapped[str] = mapped_column(String(30))
    dishes: Mapped[List["Dishes"]] = relationship()

class Ingredient(Base):
    __tablename__ = "ingredient"
    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    name: Mapped[str] = mapped_column(String(30))

class Technique(Base):
    __tablename__ = "technique"
    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    name: Mapped[str] = mapped_column(String(30))

from sqlalchemy import create_engine
engine = create_engine("sqlite:///../data_sql.db", echo=True)

Base.metadata.create_all(engine)

import os
from sqlalchemy.orm import Session

restaurant_json_dir = '../HackapizzaDataset/Menu/output/restaurants'
dishes_json_dir = '../HackapizzaDataset/Menu/output/dishes'

with Session(engine) as session:
    restaurants_to_process = os.listdir(restaurant_json_dir)
    restaurant_objs = []
    for restaurant_json in restaurants_to_process:
        if restaurant_json.endswith(".json"):
            with open(os.path.join(restaurant_json_dir, restaurant_json), 'r') as f:
                restaurant_data = json.load(f)["llm_generated"]

            with open(os.path.join(dishes_json_dir, restaurant_json), 'r') as f:
                dishes_data_raw = json.load(f)
                dishes_data = [x["llm_generated"] for x in dishes_data_raw]

            restaurant_objs.append(Restaurant(name=restaurant_data["name"],
                                              chef=restaurant_data["chef"],
                                              location=restaurant_data["location"],
                                              dishes=[Dishes(name=x["name"],
                                                             ingredients=[Ingredient(name=ing) for ing in x["ingredients"]],
                                                             techniques=[Technique(name=tec) for tec in x["techniques"]]) for x in dishes_data if x is not None]))

    session.add_all(restaurant_objs)
    session.commit()