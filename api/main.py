from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from expert_estimate.io import read_data
from .adapter import parse_raw_text, run_full_analysis
from .schemas import AnalyzeRequest, AnalyzeResponse

app = FastAPI(
    title="MMACC_LB1 Expert Estimate API",
    description="REST API для математического анализа экспертных оценок и медианы Кемени",
    version="1.0.0",
)

# CORS middleware for React Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "expert-estimate-api", "version": "1.0.0"}


@app.get("/api/example")
def get_examples():
    """Возвращает содержимое доступных примеров input.txt и input_v2.txt."""
    examples = {}
    p1 = BASE_DIR / "input.txt"
    p2 = BASE_DIR / "input_v2.txt"

    if p1.exists():
        examples["default"] = {
            "title": "Вариант по умолчанию (6 экспертов, 5 объектов)",
            "content": p1.read_text(encoding="utf-8").strip(),
        }
    if p2.exists():
        examples["v2"] = {
            "title": "Тестовый вариант 2 (5 экспертов, 5 объектов)",
            "content": p2.read_text(encoding="utf-8").strip(),
        }

    return {"examples": examples}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Анализ экспертных оценок: принимает либо текстовый блок (по строкам),
    либо список списков строк ранжирований.
    """
    raw_table: Dict[int, List[str]] = {}

    if req.rankings:
        for idx, r in enumerate(req.rankings, start=1):
            cleaned = [str(item).strip() for item in r if str(item).strip()]
            if cleaned:
                raw_table[idx] = cleaned
    elif req.text:
        raw_table = parse_raw_text(req.text)
    else:
        # По умолчанию читаем input.txt если запрос пустой
        p = BASE_DIR / "input.txt"
        if p.exists():
            raw_table = read_data(str(p))

    if not raw_table:
        raise HTTPException(
            status_code=400,
            detail="Не предоставлены корректные данные для анализа",
        )

    # Проверка консистентности: у каждого эксперта должны быть одинаковые объекты
    first_expert_objs = set(next(iter(raw_table.values())))
    for k, objs in raw_table.items():
        if set(objs) != first_expert_objs:
            raise HTTPException(
                status_code=400,
                detail=f"Несоответствие объектов у эксперта {k}: наборы объектов у всех экспертов должны совпадать!",
            )
        if len(objs) != len(set(objs)):
            raise HTTPException(
                status_code=400,
                detail=f"Дубликаты объектов в ранжировке эксперта {k}!",
            )

    try:
        return run_full_analysis(raw_table)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@app.post("/api/analyze/file", response_model=AnalyzeResponse)
async def analyze_file(file: UploadFile = File(...)):
    """Анализ загруженного текстового файла с ранжировками."""
    contents = await file.read()
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        text = contents.decode("cp1251", errors="replace")

    raw_table = parse_raw_text(text)
    if not raw_table:
        raise HTTPException(
            status_code=400,
            detail="Файл пуст или имеет некорректный формат",
        )

    first_objs = set(next(iter(raw_table.values())))
    for k, objs in raw_table.items():
        if set(objs) != first_objs:
            raise HTTPException(
                status_code=400,
                detail=f"Несоответствие объектов у эксперта {k}: наборы объектов должны быть одинаковыми.",
            )

    try:
        return run_full_analysis(raw_table)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


# Обслуживание статических файлов собранного фронтенда
from fastapi.staticfiles import StaticFiles

frontend_dist = BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


def run_server():
    """Вспомогательная функция для запуска uvicorn."""
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run_server()
