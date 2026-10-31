"""Local Tabler component playground; no external services required."""
import csv
import io
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE = Path(__file__).resolve().parent
DB = Path(os.getenv("TABLER_DB", str(BASE.parent / "data" / "demo.sqlite3")))
STATUSES = {"active": ("В работе", "purple"), "done": ("Завершён", "green"), "review": ("На проверке", "orange")}
NAMES = ["Обновление дизайн-системы", "Личный кабинет", "Мобильное приложение", "Аналитика продаж", "База знаний", "Новый онбординг", "Платёжный модуль", "Каталог продуктов", "Центр уведомлений", "Интеграция CRM", "Панель мониторинга", "Редизайн профиля", "Поиск по документам", "API партнёров", "Календарь команды", "Отчёты за квартал", "Страница настроек", "Сервис поддержки"]
PEOPLE = [("Анна Смирнова", "АС", "purple"), ("Михаил Волков", "МВ", "azure"), ("Елена Ким", "ЕК", "pink"), ("Денис Орлов", "ДО", "teal")]
ACTIVITY = [("АС", "purple", "Анна обновила дизайн-систему", "Добавлены новые компоненты", "2 мин назад"), ("МВ", "azure", "Михаил завершил задачу", "Интеграция платёжного модуля", "18 мин назад"), ("ЕК", "pink", "Елена оставила комментарий", "«Отлично, можно передавать в разработку»", "42 мин назад"), ("ДО", "teal", "Денис создал проект", "Панель мониторинга", "1 час назад"), ("АС", "purple", "Анна загрузила макеты", "12 файлов · Дизайн личного кабинета", "2 часа назад"), ("МВ", "azure", "Михаил обновил документацию", "Описание API партнёров", "3 часа назад")]

@contextmanager
def database():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.create_function("CASEFOLD", 1, lambda text: text.casefold())
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()

@asynccontextmanager
async def lifespan(app):
    DB.parent.mkdir(parents=True, exist_ok=True)
    with database() as db:
        db.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT NOT NULL, owner INTEGER NOT NULL, status TEXT NOT NULL, progress INTEGER NOT NULL, budget INTEGER NOT NULL)")
        if not db.execute("SELECT count(*) FROM projects").fetchone()[0]:
            db.executemany("INSERT INTO projects (name, owner, status, progress, budget) VALUES (?, ?, ?, ?, ?)", [(n, i % 4, list(STATUSES)[i % 3], 100 if i % 3 == 1 else (24 + i * 13) % 90, 45000 + i * 12500) for i, n in enumerate(NAMES)])
    yield

app = FastAPI(title="Tabler Lab", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
templates.env.globals.update(statuses=STATUSES, people=PEOPLE)

def project_context(q="", status="", page=1, sort="new"):
    conditions, args = [], []
    if q:
        conditions.append("CASEFOLD(name) LIKE CASEFOLD(?) ESCAPE '\\'")
        args.append("%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%")
    if status in STATUSES:
        conditions.append("status = ?")
        args.append(status)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    order = {"new": "id DESC", "name": "name COLLATE NOCASE ASC", "progress": "progress DESC"}.get(sort, "id DESC")
    with database() as db:
        total = db.execute("SELECT count(*) FROM projects" + where, args).fetchone()[0]
        pages = max(1, (total + 4) // 5)
        page = max(1, min(page, pages))
        rows = db.execute("SELECT * FROM projects" + where + " ORDER BY " + order + " LIMIT 5 OFFSET ?", [*args, (page - 1) * 5]).fetchall()
    return dict(projects=rows, total=total, pages=pages, page=page, q=q, status=status, sort=sort)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {**project_context(), "activities": ACTIVITY[:3]})

@app.get("/partials/projects", response_class=HTMLResponse)
def projects(request: Request, q: str = Query("", max_length=200), status: str = "", page: int = Query(1, ge=1), sort: str = "new"):
    return templates.TemplateResponse(request, "partials/projects.html", project_context(q, status, page, sort))

@app.post("/projects", response_class=HTMLResponse)
def create_project(request: Request, name: str = Form(""), owner: str = Form("0"), status: str = Form("active")):
    name = name.strip()
    errors = []
    if not 3 <= len(name) <= 100:
        errors.append("Название должно содержать от 3 до 100 символов.")
    if owner not in {"0", "1", "2", "3"}:
        errors.append("Выберите участника команды.")
    if status not in STATUSES:
        errors.append("Выберите статус из списка.")
    if errors:
        return templates.TemplateResponse(request, "partials/form-result.html", {"errors": errors})
    with database() as db:
        db.execute("INSERT INTO projects (name, owner, status, progress, budget) VALUES (?, ?, ?, ?, ?)", (name, int(owner), status, 100 if status == "done" else 0, 0))
    return templates.TemplateResponse(request, "partials/form-result.html", {"name": name}, headers={"HX-Trigger": "projectCreated"})

@app.get("/partials/activity", response_class=HTMLResponse)
def activity(request: Request, expanded: bool = False):
    return templates.TemplateResponse(request, "partials/activity.html", {"activities": ACTIVITY if expanded else ACTIVITY[:3], "expanded": expanded})

@app.get("/export.csv")
def export():
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["ID", "Проект", "Ответственный", "Статус", "Прогресс", "Бюджет"])
    with database() as db:
        for row in db.execute("SELECT * FROM projects ORDER BY id DESC"):
            # Prevent spreadsheet formula execution for user-provided names.
            name = row["name"]
            if name.startswith(("=", "+", "-", "@", "\t", "\r", "\n")):
                name = "'" + name
            writer.writerow([row["id"], name, PEOPLE[row["owner"]][0], STATUSES[row["status"]][0], row["progress"], row["budget"]])
    return Response("\ufeff" + stream.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="projects.csv"'})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.middleware("http")
async def local_resources_only(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    return response
