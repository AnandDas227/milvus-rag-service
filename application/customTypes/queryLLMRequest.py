from pydantic import BaseModel, Field
from typing import Optional, List


class queryLLMRequest(BaseModel):
    question: str = Field(title="Enter you question for the LLM", description="Enter you question for the LLM")
    num_results: Optional[str] = Field(default="2")
    min_score: Optional[str] = Field(default="5")

    