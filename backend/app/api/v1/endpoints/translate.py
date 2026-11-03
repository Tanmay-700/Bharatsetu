from fastapi import APIRouter
from app.schemas.schemas import TranslationRequest, TranslationResponse
from app.services.translation.translator import translation_service

router = APIRouter(prefix="/translate", tags=["Translation"])

@router.post("", response_model=TranslationResponse)
async def translate_passage(req: TranslationRequest):
    """
    Dedicated endpoint for translating text passages into one of the 8 supported languages.
    """
    result = await translation_service.translate_text(
        text=req.text,
        source_lang=req.source_language or "auto",
        target_lang=req.target_language
    )
    return TranslationResponse(**result)
