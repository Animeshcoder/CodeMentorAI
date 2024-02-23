from typing import List, Dict
from pydantic import BaseModel, Field

class CodeCheckResponse(BaseModel):
    correctness: str  # Either "Correct" or "Incorrect"
    explanation: str  # Detailed explanation if incorrect
    efficiency: str  # Comments on efficiency of code

    

