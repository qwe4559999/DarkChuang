from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid
import os
from app.core.config import settings

router = APIRouter()

UPLOAD_DIR = Path("data/uploads/chat_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image for chat analysis.
    Returns the local file path.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return relative path or absolute path depending on what the backend needs
        # Returning absolute path for internal use
        return {
            "filename": filename,
            "file_path": str(file_path.absolute()),
            "url": f"/uploads/chat_images/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
