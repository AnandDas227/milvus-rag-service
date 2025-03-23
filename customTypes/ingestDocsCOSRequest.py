from pydantic import BaseModel, Field
from typing import Optional, List


class ingestDocsCOSRequest(BaseModel):
    chunk_size: Optional[str] = Field(default="512")
    chunk_overlap: Optional[str] = Field(default="256")
    