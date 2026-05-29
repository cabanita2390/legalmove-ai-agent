import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.main import langfuse, run_pipeline, validate_environment

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

app = FastAPI(
    title="LegalMove AI Agent API",
    description="API para análisis de contratos originales vs enmiendas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_image_upload(file: UploadFile, field_name: str) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail=f"El archivo '{field_name}' no tiene nombre.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido en '{field_name}'. Use: .jpg, .jpeg o .png",
        )
    return ext


async def _save_upload(file: UploadFile, dest_path: Path) -> None:
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo '{file.filename}' supera el límite de 10 MB.",
        )
    dest_path.write_bytes(content)


@app.on_event("startup")
def on_startup() -> None:
    validate_environment(raise_on_missing_openai=True)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "legalmove-ai-agent"}


@app.post("/api/analyze")
async def analyze(
    original: UploadFile = File(..., description="Imagen del contrato original"),
    amendment: UploadFile = File(..., description="Imagen de la enmienda o adenda"),
) -> dict:
    original_ext = _validate_image_upload(original, "original")
    amendment_ext = _validate_image_upload(amendment, "amendment")

    temp_dir = tempfile.mkdtemp(prefix="legalmove_")
    original_path = Path(temp_dir) / f"original{original_ext}"
    amendment_path = Path(temp_dir) / f"amendment{amendment_ext}"

    try:
        await _save_upload(original, original_path)
        await _save_upload(amendment, amendment_path)

        result = run_pipeline(str(original_path), str(amendment_path))
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        langfuse.flush()
        shutil.rmtree(temp_dir, ignore_errors=True)


if FRONTEND_DIST.is_dir():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")

        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        index_path = FRONTEND_DIST / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Frontend build not found")
