from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/unblocker")
async def unblock(request: Request, url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return HTMLResponse(content=response.text, status_code=response.status_code)
