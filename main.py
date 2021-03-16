import pkg_resources
from typing import List

from fastapi import FastAPI, UploadFile
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse

from instagrapi import Client
from instagrapi.types import (Location, Media, Story, StoryHashtag, StoryLink,
                              StoryLocation, StoryMention, StorySticker,
                              Usertag)

app = FastAPI()
cl = Client()


@app.get("/media/pk_from_code", tags=["media"])
async def media_pk_from_code(code: str) -> int:
    """Get media pk from code
    """
    return cl.media_pk_from_code(code)


@app.get("/media/info", response_model=Media, tags=["media"])
async def media_info(pk: int) -> Media:
    """Get media info by pk
    """
    return cl.media_info(pk)


@app.get("/", tags=["system"])
async def root():
    return RedirectResponse(url="/docs")


@app.get("/version", tags=["system"])
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
