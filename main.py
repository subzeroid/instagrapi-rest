import pkg_resources

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from instagrapi import Client

app = FastAPI()
cl = Client()


@app.get("/")
async def root():
    return "Open http://localhost:8000/docs"


@app.get("/media/pk_from_code")
async def media_pk_from_code(code: str) -> int:
    """Get media pk from code
    """
    return cl.media_pk_from_code(code)


@app.get("/version")
async def version():
    """Return package versions
    """
    versions = {}
    for name in ('instagrapi', ):
        item = pkg_resources.require(name)
        if item:
            versions[name] = item[0].version
    return versions


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="instagrapi-rest",
        version="1.0.0",
        description="RESTful API Service for instagrapi",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
