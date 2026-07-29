import io
import traceback
from pypdf import PdfReader
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.schemas.jd import JDTextInput
from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/jd", tags=["JD"])

_MAX_PDF_BYTES = 5 * 1024 * 1024   # 5 MB
_ALLOWED_MIME = {"application/pdf", "application/octet-stream"}


@router.post("/upload")
async def upload_jd_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"[jd/upload] filename={file.filename} content_type={file.content_type}")

    if file.content_type not in _ALLOWED_MIME:
        print(f"[jd/upload] REJECTED mime: {file.content_type}")
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    print(f"[jd/upload] read {len(contents)} bytes")

    if len(contents) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5 MB.")

    try:
        reader = PdfReader(io.BytesIO(contents))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        print(f"[jd/upload] extracted {len(text)} chars from {len(reader.pages)} pages")
    except Exception as e:
        print(f"[jd/upload] pypdf error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="PDF appears to be empty or contains only images.")

    return {"jd_text": text, "filename": file.filename}


@router.post("/text")
def submit_jd_text(payload: JDTextInput):
    """
    Submit a JD as plain text. Validates and echoes back the text and platform scope.
    The frontend uses this to confirm the input before triggering /search.
    """
    return {"jd_text": payload.jd_text, "platform_scope": payload.platform_scope}
