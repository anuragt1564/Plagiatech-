from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/check-plagiarism")
async def check_plagiarism(input: TextInput):
    # Integrate with Copyleaks or PlagScan API
    try:
        # Simulate API call
        result = {"similarity": "10%", "sources": ["link1", "link2"]}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))