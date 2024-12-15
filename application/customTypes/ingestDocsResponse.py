from pydantic import BaseModel, Field


class ingestDocsResponse(BaseModel):
    response: str
    