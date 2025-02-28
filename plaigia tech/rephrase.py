from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/rephrase")
async def rephrase_text(input: TextInput):
    # Integrate with Hugging Face or OpenAI API
    try:
        # Simulate API call
        rephrased_text = "A quick brown fox jumps over a resting dog"
        return {"rephrased_text": rephrased_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))