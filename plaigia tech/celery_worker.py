from celery import Celery
import os
import httpx
import time
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get Redis URL from environment variable or use default
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_concurrency=4,
)

# Cache for storing results (in production, use Redis)
result_cache = {}

@celery_app.task(bind=True, name="check_plagiarism_task")
def check_plagiarism_task(self, text: str) -> Dict[str, Any]:
    """
    Check text for plagiarism using external API.
    
    Args:
        text: The text to check for plagiarism
        
    Returns:
        Dict containing percentage and sources
    """
    task_id = self.request.id
    logger.info(f"Starting plagiarism check task {task_id}")
    
    # Check cache first
    cache_key = f"plagiarism:{hash(text)}"
    if cache_key in result_cache:
        logger.info(f"Cache hit for task {task_id}")
        return result_cache[cache_key]
    
    try:
        # In production, integrate with Copyleaks or PlagScan API
        # api_key = os.getenv("COPYLEAKS_API_KEY")
        # headers = {"Authorization": f"Bearer {api_key}"}
        
        # Simulate API call with delay
        logger.info(f"Calling external plagiarism API for task {task_id}")
        time.sleep(2)  # Simulate API delay
        
        # Simulated result
        result = {
            "percentage": 10.5,
            "sources": [
                "https://example.com/source1",
                "https://example.com/source2"
            ]
        }
        
        # Cache the result
        result_cache[cache_key] = result
        
        logger.info(f"Completed plagiarism check task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in plagiarism check task {task_id}: {str(e)}")
        self.retry(exc=e, countdown=5, max_retries=3)

@celery_app.task(bind=True, name="rephrase_text_task")
def rephrase_text_task(self, text: str) -> str:
    """
    Rephrase text using AI model.
    
    Args:
        text: The text to rephrase
        
    Returns:
        Rephrased text
    """
    task_id = self.request.id
    logger.info(f"Starting text rephrasing task {task_id}")
    
    # Check cache first
    cache_key = f"rephrase:{hash(text)}"
    if cache_key in result_cache:
        logger.info(f"Cache hit for task {task_id}")
        return result_cache[cache_key]
    
    try:
        # In production, integrate with OpenAI or Hugging Face API
        # api_key = os.getenv("OPENAI_API_KEY")
        # headers = {"Authorization": f"Bearer {api_key}"}
        
        # Simulate API call with delay
        logger.info(f"Calling external rephrasing API for task {task_id}")
        time.sleep(2)  # Simulate API delay
        
        # Simulated result
        rephrased = "The swift brown fox leaps over the idle dog."
        
        # Cache the result
        result_cache[cache_key] = rephrased
        
        logger.info(f"Completed text rephrasing task {task_id}")
        return rephrased
        
    except Exception as e:
        logger.error(f"Error in text rephrasing task {task_id}: {str(e)}")
        self.retry(exc=e, countdown=5, max_retries=3)
