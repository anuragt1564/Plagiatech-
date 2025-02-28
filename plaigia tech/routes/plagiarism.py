from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import httpx
import asyncio
import logging
from celery_worker import check_plagiarism_task
from config import settings
from auth import get_current_user, UserInDB, fake_users_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["plagiarism"])

# Models
class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=settings.MAX_TEXT_LENGTH)
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v

class PlagiarismResult(BaseModel):
    percentage: float
    sources: List[str]

class PlagiarismTask(BaseModel):
    task_id: str
    status: str

# In-memory task storage (use Redis in production)
task_store: Dict[str, Dict[str, Any]] = {}

# Routes
@router.post("/check-plagiarism", response_model=PlagiarismResult)
async def check_plagiarism(
    input: TextInput,
    background_tasks: BackgroundTasks,
    current_user: Optional[UserInDB] = Depends(get_current_user)
):
    """
    Check text for plagiarism using external API.
    
    Returns percentage of plagiarism and list of sources.
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
        # task = check_plagiarism_task.delay(input.text)
        # task_id = task.id
        # task_store[task_id] = {"status": "processing"}
        # return {"task_id": task_id, "status": "processing"}
        
        # Simulate API call to Copyleaks
        logger.info("Checking text for plagiarism")
        
        # In production, use actual API with proper authentication
        # api_key = settings.COPYLEAKS_API_KEY
        
        # Simulating API call for now
        # In production, replace with actual API call
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         "https://api.copyleaks.com/v3/plagiarism/check",
        #         headers={"Authorization": f"Bearer {api_key}"},
        #         json={"text": input.text}
        #     )
        #     if response.status_code != 200:
        #         raise HTTPException(
        #             status_code=response.status_code,
        #             detail=f"Plagiarism API error: {response.text}"
        #         )
        #     result = response.json()
        
        # Simulated result
        await asyncio.sleep(1)  # Simulate API delay
        result = {
            "percentage": 10.5, 
            "sources": [
                "https://example.com/source1", 
                "https://example.com/source2"
            ]
        }
        
        logger.info(f"Plagiarism check completed: {result['percentage']}%")
        return result
        
    except HTTPException as e:
        logger.error(f"HTTP error in plagiarism check: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error checking plagiarism: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking plagiarism: {str(e)}"
        )

@router.get("/check-plagiarism/{task_id}", response_model=PlagiarismResult)
async def get_plagiarism_result(task_id: str):
    """
    Get the result of an asynchronous plagiarism check task.
    """
    # In production, check Celery task status
    # task = check_plagiarism_task.AsyncResult(task_id)
    # if task.state == 'PENDING':
    #     return JSONResponse({"task_id": task_id, "status": "processing"})
    # elif task.state == 'SUCCESS':
    #     return task.result
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
