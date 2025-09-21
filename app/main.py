from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiofiles
import os
import tempfile
import shutil
from typing import Optional

from .chapter_translate import translate_chapter
from .novel_translate import translate_novel
from .detect_lang import detect_language
from .utils import read_text, write_text

app = FastAPI(title="Novel Translator", description="Translate chapters and novels using ONNX models")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ru": "Russian"
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with navigation to chapter or novel translation"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chapter", response_class=HTMLResponse)
async def chapter_page(request: Request):
    """Chapter translation page"""
    return templates.TemplateResponse("chapter.html", {
        "request": request,
        "languages": SUPPORTED_LANGUAGES
    })

@app.get("/novel", response_class=HTMLResponse)
async def novel_page(request: Request):
    """Novel translation page"""
    return templates.TemplateResponse("novel.html", {
        "request": request,
        "languages": SUPPORTED_LANGUAGES
    })

@app.post("/translate-chapter")
async def translate_chapter_endpoint(
    request: Request,
    target_lang: str = Form(...),
    text_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Translate a single chapter from text input or uploaded file"""
    try:
        # Get text content
        if file:
            content = await file.read()
            text = content.decode('utf-8')
        elif text_input:
            text = text_input
        else:
            return templates.TemplateResponse("chapter.html", {
                "request": request,
                "languages": SUPPORTED_LANGUAGES,
                "error": "Please provide text or upload a file"
            })

        # Detect source language
        source_lang = detect_language(text)
        
        # Create temporary file for translation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(text)
            temp_path = temp_file.name

        try:
            # Translate the chapter
            translated_text = translate_chapter(temp_path, target_lang)
            
            return templates.TemplateResponse("chapter.html", {
                "request": request,
                "languages": SUPPORTED_LANGUAGES,
                "original_text": text,
                "translated_text": translated_text,
                "source_lang": SUPPORTED_LANGUAGES.get(source_lang, source_lang),
                "target_lang": SUPPORTED_LANGUAGES.get(target_lang, target_lang),
                "success": True
            })
        finally:
            os.unlink(temp_path)

    except Exception as e:
        return templates.TemplateResponse("chapter.html", {
            "request": request,
            "languages": SUPPORTED_LANGUAGES,
            "error": f"Translation error: {str(e)}"
        })

@app.post("/translate-novel")
async def translate_novel_endpoint(
    request: Request,
    target_lang: str = Form(...),
    file: UploadFile = File(...)
):
    """Translate an entire novel from uploaded ZIP file"""
    try:
        # Save uploaded ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            content = await file.read()
            temp_zip.write(content)
            zip_path = temp_zip.name

        try:
            # Translate the novel
            translated_zip_path = translate_novel(zip_path, target_lang)
            
            # Return the translated ZIP file
            return FileResponse(
                translated_zip_path,
                filename="translated_novel.zip",
                media_type="application/zip"
            )
        finally:
            os.unlink(zip_path)

    except Exception as e:
        return templates.TemplateResponse("novel.html", {
            "request": request,
            "languages": SUPPORTED_LANGUAGES,
            "error": f"Translation error: {str(e)}"
        })

@app.post("/download-chapter")
async def download_chapter(text: str = Form(...), filename: str = Form("translated_chapter.txt")):
    """Download translated chapter as text file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(text)
        temp_path = temp_file.name

    return FileResponse(
        temp_path,
        filename=filename,
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)