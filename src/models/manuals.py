from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class LicenseLevel(BaseModel):
    level: str
    level_description: str


class LicenseCategory(BaseModel):
    name: str
    available_levels: List[LicenseLevel]


class License(BaseModel):
    available_categories: List[LicenseCategory]
