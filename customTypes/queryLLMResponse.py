from pydantic import BaseModel

class queryLLMResponse(BaseModel):
    response: str