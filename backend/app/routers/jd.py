import fitz  # PyMuPDF
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.jd import JDTextInput

router = APIRouter(prefix="/jd", tags=["JD"])

_MAX_PDF_BYTES = 5 * 1024 * 1024   # 5 MB
_ALLOWED_MIME = {"application/pdf", "application/octet-stream"}


@router.post("/upload")
async def upload_jd_pdf(file: UploadFile = File(...)):
    """
    Upload a JD as a PDF. Returns the extracted plain text.
    Accepts: application/pdf, max 5 MB.
    """
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()

    if len(contents) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5 MB.")

    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    text = text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="PDF appears to be empty or contains only images (no extractable text).",
        )

    return {"jd_text": text, "filename": file.filename}


@router.post("/text")
def submit_jd_text(payload: JDTextInput):
    """
    Submit a JD as plain text. Validates and echoes back the text and platform scope.
    The frontend uses this to confirm the input before triggering /search.
    """
    return {"jd_text": payload.jd_text, "platform_scope": payload.platform_scope}
