from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from rag_agent import get_ragagent_response
from sme_db_agent import get_dbagent_response

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/dbagent/{query}", response_class=JSONResponse)
async def read_item(request: Request, query: str):
    res = get_dbagent_response(query)

    return res

@app.get("/ragagent/{query}", response_class=JSONResponse)
async def read_item(request: Request, query: str):
    res = get_ragagent_response(query)

    return res


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )