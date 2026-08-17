"""C 语言学习平台后端：课程数据 + 进度跟踪(SQLite) + C 判题。

启动：uv run uvicorn app.main:app --reload --port 8000
（或 .venv 激活后：uvicorn app.main:app --reload）
"""
import json
import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .judge import EXERCISES, judge, load_tests, run_manual

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
DB_PATH = DATA_DIR / "progress.db"

app = FastAPI(title="C 语言学习平台")


# ---------- 数据库 ----------

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                lesson_id TEXT PRIMARY KEY,
                done       INTEGER NOT NULL DEFAULT 0,
                best_score INTEGER NOT NULL DEFAULT -1,
                attempts   INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT
            )
        """)


@app.on_event("startup")
def _startup():
    init_db()


# ---------- 课程数据 ----------

def load_lessons() -> dict:
    return json.loads((DATA_DIR / "lessons.json").read_text(encoding="utf-8"))


def get_lesson(lesson_id: str) -> dict | None:
    for chapter in load_lessons()["chapters"]:
        for lesson in chapter["lessons"]:
            if lesson["id"] == lesson_id:
                return lesson
    return None


# ---------- API ----------

class CodeIn(BaseModel):
    code: str


class RunIn(BaseModel):
    code: str
    input: str = ""


class DoneIn(BaseModel):
    done: bool


def _progress_map() -> dict:
    with get_db() as con:
        rows = con.execute("SELECT * FROM progress").fetchall()
    return {r["lesson_id"]: dict(r) for r in rows}


@app.get("/api/lessons")
def api_lessons():
    data = load_lessons()
    progress = _progress_map()
    return {"chapters": data["chapters"], "progress": progress}


@app.get("/api/lesson/{lesson_id}")
def api_lesson(lesson_id: str):
    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(404, "课时不存在")
    workdir = EXERCISES / lesson_id
    code = (workdir / "main.c").read_text(encoding="utf-8") if (workdir / "main.c").exists() else None
    return {
        "lesson": lesson,
        "code": code,
        "tests": load_tests(lesson_id),
        "progress": _progress_map().get(lesson_id),
    }


@app.put("/api/lesson/{lesson_id}/code")
def api_save_code(lesson_id: str, body: CodeIn):
    if get_lesson(lesson_id) is None:
        raise HTTPException(404, "课时不存在")
    workdir = EXERCISES / lesson_id
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "main.c").write_text(body.code, encoding="utf-8")
    return {"ok": True}


@app.post("/api/lesson/{lesson_id}/judge")
def api_judge(lesson_id: str, body: CodeIn):
    if get_lesson(lesson_id) is None:
        raise HTTPException(404, "课时不存在")
    result = judge(lesson_id, body.code)
    if result["score"] >= 0:
        with get_db() as con:
            row = con.execute("SELECT * FROM progress WHERE lesson_id=?", (lesson_id,)).fetchone()
            best = result["score"] if row is None or result["score"] > row["best_score"] else row["best_score"]
            con.execute(
                """INSERT INTO progress (lesson_id, done, best_score, attempts, updated_at)
                   VALUES (?, 0, ?, 1, ?)
                   ON CONFLICT(lesson_id) DO UPDATE SET
                       best_score=excluded.best_score,
                       attempts=attempts+1,
                       updated_at=excluded.updated_at""",
                (lesson_id, best, time.strftime("%Y-%m-%d %H:%M")),
            )
    return result


@app.post("/api/lesson/{lesson_id}/run")
def api_run(lesson_id: str, body: RunIn):
    if get_lesson(lesson_id) is None:
        raise HTTPException(404, "课时不存在")
    return run_manual(lesson_id, body.code, body.input)


@app.post("/api/lesson/{lesson_id}/done")
def api_done(lesson_id: str, body: DoneIn):
    if get_lesson(lesson_id) is None:
        raise HTTPException(404, "课时不存在")
    with get_db() as con:
        con.execute(
            """INSERT INTO progress (lesson_id, done, best_score, attempts, updated_at)
               VALUES (?, ?, -1, 0, ?)
               ON CONFLICT(lesson_id) DO UPDATE SET done=excluded.done, updated_at=excluded.updated_at""",
            (lesson_id, 1 if body.done else 0, time.strftime("%Y-%m-%d %H:%M")),
        )
    return {"ok": True}


# 前端静态文件（放在最后，避免挡住 API 路由）
app.mount("/", StaticFiles(directory=BASE / "static", html=True), name="static")
