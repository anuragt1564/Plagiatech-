from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import httpx
import asyncio
import logging
from celery_worker import rephrase_text_task
from config import settings
from auth import get_current_user, UserInDB, fake_users_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["rephrase"])

# Models
class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=settings.MAX_TEXT_LENGTH)
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v

class RephraseResult(BaseModel):
    original: str
    rephrased: str

class RephraseTask(BaseModel):
    task_id: str
    status: str

# In-memory task storage (use Redis in production)
task_store: Dict[str, Dict[str, Any]] = {}

# Routes
@router.post("/rephrase", response_model=RephraseResult)
async def rephrase_text(
    input: TextInput,
    background_tasks: BackgroundTasks,
    current_user: Optional[UserInDB] = Depends(get_current_user)
):
    """
    Rephrase text using AI model.
    
    Returns original text and rephrased version.
    """
    try:
        # Validate input
        if len(input.text) > settings.MAX_TEXT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Text too long (max {settings.MAX_TEXT_LENGTH} characters)"
            )
        
        # Check user limits if authenticated
        if current_user:
            # In production, check user's usage count against their tier limit
            user_dict = fake_users_db.get(current_user.username, {})
            usage_count = user_dict.get("usage_count", 0)
            is_premium = user_dict.get("is_premium", False)
            
            if not is_premium and usage_count >= 10:  # Free tier limit
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Free tier limit reached. Please upgrade to premium."
                )
            
            # Increment usage count
            user_dict["usage_count"] = usage_count + 1
        
        # For demonstration, we'll use direct API call
        # In production, use Celery for async processing
        # task = rephrase_text_task.delay(input.text)
        # task_id = task.id
        # task_store[task_id] = {"status": "processing"}
        # return {"task_id": task_id, "status": "processing"}
        
        # Simulate API call to OpenAI or Hugging Face
        logger.info("Rephrasing text")
        
        # In production, use actual API with proper authentication
        # api_key = settings.OPENAI_API_KEY
        
        # Simulating API call for now
        # In production, replace with actual API call
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         "https://api.openai.com/v1/chat/completions",
        #         headers={"Authorization": f"Bearer {api_key}"},
        #         json={
        #             "model": "gpt-3.5-turbo",
        #             "messages": [
        #                 {"role": "system", "content": "You are a helpful assistant that rephrases text."},
        #                 {"role": "user", "content": f"Rephrase the following text while preserving its meaning: {input.text}"}
        #             ],
        #             "temperature": 0.7,
        #             "max_tokens": 1000
        #         }
        #     )
        #     if response.status_code != 200:
        #         raise HTTPException(
        #             status_code=response.status_code,
        #             detail=f"OpenAI API error: {response.text}"
        #         )
        #     result = response.json()
        #     rephrased = result["choices"][0]["message"]["content"].strip()
        
        # Simulated result
        await asyncio.sleep(1)  # Simulate API delay
        rephrased = "The swift brown fox leaps over the idle dog."
        
        logger.info("Text rephrasing completed")
        return {"original": input.text, "rephrased": rephrased}
        
    except HTTPException as e:
        logger.error(f"HTTP error in text rephrasing: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error rephrasing text: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rephrasing text: {str(e)}"
        )

@router.get("/rephrase/{task_id}", response_model=RephraseResult)
async def get_rephrase_result(task_id: str):
    """
    Get the result of an asynchronous text rephrasing task.
    """
    # In production, check Celery task status
    # task = rephrase_text_task.AsyncResult(task_id)
    # if task.state == 'PENDING':
    #     return JSONResponse({"task_id": task_id, "status": "processing"})
    # elif task.state == 'SUCCESS':
    #     return {"original": task.result["original"], "rephrased": task.result["rephrased"]}
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Task failed: {task.info}"
    #     )
    
    # For demonstration
    if task_id not in task_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task_info = task_store[task_id]
    if task_info["status"] == "processing":
        return JSONResponse({"task_id": task_id, "status": "processing"})
    elif task_info["status"] == "completed":
        return task_info["result"]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task failed: {task_info.get('error', 'Unknown error')}"
        )
