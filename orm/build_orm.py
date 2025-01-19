from typing import Optional, List
from sqlalchemy import ForeignKey, Table
from sqlalchemy import String, text, Column, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import pandas as pd
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
    licenses: Mapped[List["License"]|None] = relationship()
    dishes: Mapped[List["Dishes"]] = relationship()


class AllowedTechniques(Base):
    __tablename__ = 'allowed_techniques'

    license_id = Column(Integer, ForeignKey('license.id'), primary_key=True)
    technique_id = Column(Integer, ForeignKey('technique.id'), primary_key=True)

    # Extra columns
    allowed = Column(Boolean, default=True)
    # Reference back to parent tables
    license = relationship("License", back_populates="allowed_licenses")
    technique = relationship("Technique", back_populates="allowed_techniques")

class Technique(Base):
    __tablename__ = "technique"
    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    name: Mapped[str] = mapped_column(String(30))
    allowed_techniques = relationship("AllowedTechniques", back_populates="technique")
class License(Base):
    __tablename__ = "license"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    level: Mapped[int] = mapped_column(Integer)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"))
    allowed_licenses = relationship("AllowedTechniques", back_populates="license")


class Ingredient(Base):
    __tablename__ = "ingredient"
    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    name: Mapped[str] = mapped_column(String(30))



# class LicenseAllowed(Base):
#     __tablename__ = "license_allowed"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     license_id: Mapped[id] = mapped_column(ForeignKey("license.id"))
#     technique_id: Mapped[id] = mapped_column(ForeignKey("technique.id"))
#     allowed: Mapped[bool | None] = Column(Boolean)


class LocationDistances(Base):
    __tablename__ = "location_distances"
    id: Mapped[int] = mapped_column(primary_key=True)
    _from: Mapped[str] = mapped_column(ForeignKey("restaurant.location"))
    _to: Mapped[str] = mapped_column(ForeignKey("restaurant.location"))
    distance: Mapped[int] = mapped_column(Integer)

from sqlalchemy import create_engine
engine = create_engine("sqlite:///../data_sql_2.db", echo=True)

Base.metadata.create_all(engine)

import os
from sqlalchemy.orm import Session

restaurant_json_dir = '../HackapizzaDataset/Menu/output/restaurants'
dishes_json_dir = '../HackapizzaDataset/Menu/output/dishes'
license_level_mapping = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
    'V': 5,
    'VI': 6,
    'VII': 7,
    'UNKNOWN': -1
}
with open('../notebooks/restaurant_licence_classification.json', 'r') as f:
    restaurant_licenses = json.load(f)

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

            if restaurant_data:
                restaurant_objs.append(Restaurant(name=restaurant_data["name"],
                                                  chef=restaurant_data["chef"],
                                                  location=restaurant_data["location"],
                                                  licenses=[License(name=x["licence_type"], level=license_level_mapping.get(x["licence_level"], x["licence_level"])) for x in restaurant_licenses[0].get(restaurant_data["name"], [])],
                                                  dishes=[Dishes(name=x["name"],
                                                                 ingredients=[Ingredient(name=ing) for ing in x["ingredients"]],
                                                                 techniques=[Technique(name=tec) for tec in x["techniques"]]) for x in dishes_data if x is not None]))

    session.add_all(restaurant_objs)
    session.commit()

# ingest location distances
with Session(engine) as session:

    df = pd.read_csv("../ingestor/distanze_transformed.csv")
    df_records = df.to_dict(orient="records")

    location_distances = [LocationDistances(_from=x["From"], _to=x["To"], distance=x["Distance"]) for x in df_records]
    #
    session.add_all(location_distances)
    session.commit()

with Session(engine) as session:
    with open('../notebooks/output_flag.json', 'r') as f:
        technique_limits_json = json.load(f)
    technique_limits_json = [json.loads(x) for x in technique_limits_json]
    print(technique_limits_json)
    for tech_lim in technique_limits_json:
        licenses_id = []
        for limit in tech_lim["limits"]["licence_list"]:
            print(limit)

            license_id = session.execute(text(f"SELECT id FROM license WHERE name='{limit["licence_type"]}' AND level<'{license_level_mapping.get(limit["level"], limit["level"])}'")).fetchone()
            if license_id:
                licenses_id.append(license_id[0])
        technique_id = session.execute(text(f"SELECT id FROM technique WHERE name='{tech_lim["name"].replace("'", "''")}'")).fetchone()
        if technique_id:
            technique_id = technique_id[0]

            for license in licenses_id:
                technique_objs = [AllowedTechniques(allowed=False, license_id=license, technique_id=technique_id) for x in technique_limits_json]