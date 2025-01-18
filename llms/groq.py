from langchain_groq import ChatGroq
from pydantic import BaseModel, field_validator, model_validator
import requests

class GroqConf(BaseModel):
    api_key: str
    model: str
    temperature: float

    @field_validator("model")
    def validate_model(cls, value: str, values: dict) -> str:
        api_key = values.data["api_key"]
        available_models = cls.__get_groq_available_models(api_key=api_key)

        if value not in available_models:
            raise ValueError(f"Model not available: {value}")

        return value

    @staticmethod
    def __get_groq_available_models(api_key: str) -> list[str]:
        url = "https://api.groq.com/openai/v1/models"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        print(response)

        return [model["id"] for model in response.json()["data"]]

    @field_validator("temperature")
    def validate_temperature(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError("The temperature ranges from 0.0 to 1.0")
        return value