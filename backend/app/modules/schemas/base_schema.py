from pydantic import BaseModel
from typing import Optional


class BaseSchema(BaseModel):
    id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }
    