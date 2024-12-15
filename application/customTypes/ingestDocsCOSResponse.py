from pydantic import BaseModel, Field


class ingestDocsCOSResponse(BaseModel):
    response: str
    