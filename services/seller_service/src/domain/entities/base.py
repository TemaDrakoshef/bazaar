from pydantic import BaseModel, ConfigDict


class CustomModel(BaseModel):
    """Custom Base pydantic model"""

    model_config = ConfigDict(from_attributes=True)
