import requests
import tempfile
import pkg_resources
from typing import List, Optional

from pydantic import HttpUrl
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse, JSONResponse

from instagrapi import Client
from instagrapi.story import StoryBuilder
from instagrapi.types import (Media, Story, StoryHashtag, StoryLink,
                              StoryLocation, StoryMention, StorySticker)
from storages import ClientStorage


app = FastAPI()
clients = ClientStorage()


@app.get("/media/pk_from_code", tags=["media"])
async def media_pk_from_code(code: str) -> int:
    """Get media pk from code
    """
    return Client().media_pk_from_code(code)


@app.get("/media/info", response_model=Media, tags=["media"])
async def media_info(pk: int) -> Media:
    """Get media info by pk
    """
    return Client().media_info(pk)


@app.post("/photo/upload_to_story", response_model=Story, tags=["upload"])
async def photo_upload_to_story(sessionid: str = Form(...),
                                file: UploadFile = File(...),
                                caption: Optional[str] = Form(''),
                                mentions: List[StoryMention] = [],
                                locations: List[StoryLocation] = [],
                                links: List[StoryLink] = [],
                                hashtags: List[StoryHashtag] = [],
                                stickers: List[StorySticker] = []
                                ) -> Story:
    """Upload photo to story
    """
    cl = clients.get(sessionid)
    with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
        data = await file.read()
        fp.write(data)
        photo = StoryBuilder(fp.name, caption, mentions).photo(15)
        result = cl.photo_upload_to_story(
            photo.path,
            caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers
        )
    return result


@app.post("/photo/upload_to_story/by_url", response_model=Story, tags=["upload"])
async def photo_upload_to_story_by_url(sessionid: str = Form(...),
                                url: HttpUrl = Form(...),
                                caption: Optional[str] = Form(''),
                                mentions: List[StoryMention] = [],
                                locations: List[StoryLocation] = [],
                                links: List[StoryLink] = [],
                                hashtags: List[StoryHashtag] = [],
                                stickers: List[StorySticker] = []
                                ) -> Story:
    """Upload photo to story by URL to file
    """
    content = requests.get(url).content
    cl = clients.get(sessionid)
    with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
        fp.write(content)
        photo = StoryBuilder(fp.name, caption, mentions).photo(15)
        result = cl.photo_upload_to_story(
            photo.path,
            caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers
        )
    return result


@app.post("/video/upload_to_story", response_model=Story, tags=["upload"])
async def video_upload_to_story(sessionid: str = Form(...),
                                file: UploadFile = File(...),
                                caption: Optional[str] = Form(''),
                                mentions: List[StoryMention] = [],
                                locations: List[StoryLocation] = [],
                                links: List[StoryLink] = [],
                                hashtags: List[StoryHashtag] = [],
                                stickers: List[StorySticker] = []
                                ) -> Story:
    """Upload video to story
    """
    cl = clients.get(sessionid)
    with tempfile.NamedTemporaryFile(suffix='.mp4') as fp:
        data = await file.read()
        fp.write(data)
        video = StoryBuilder(fp.name, caption, mentions).video(15)
        result = cl.video_upload_to_story(
            video.path,
            caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers
        )
    return result


@app.post("/video/upload_to_story/by_url", response_model=Story, tags=["upload"])
async def video_upload_to_story_by_url(sessionid: str = Form(...),
                                url: HttpUrl = Form(...),
                                caption: Optional[str] = Form(''),
                                mentions: List[StoryMention] = [],
                                locations: List[StoryLocation] = [],
                                links: List[StoryLink] = [],
                                hashtags: List[StoryHashtag] = [],
                                stickers: List[StorySticker] = []
) -> Story:
    """Upload video to story by URL to file
    """
    content = requests.get(url).content
    cl = clients.get(sessionid)
    with tempfile.NamedTemporaryFile(suffix='.mp4') as fp:
        fp.write(content)
        video = StoryBuilder(fp.name, caption, mentions).video(15)
        result = cl.video_upload_to_story(
            video.path,
            caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers
        )
    return result



@app.get("/auth/login", tags=["auth"])
async def auth_login(username: str = Form(...), password: str = Form(...), verification_code: Optional[str] = Form('')) -> str:
    """Login by username and password with 2FA
    """
    cl = clients.client()
    result = cl.login(username, password, verification_code=verification_code)
    if result:
        clients.set(cl)
        return cl.sessionid
    return result


@app.get("/", tags=["system"], summary="Redirect to /docs")
async def root():
    """Redirect to /docs
    """
    return RedirectResponse(url="/docs")


@app.get("/version", tags=["system"], summary="Get dependency versions")
async def version():
    """Get dependency versions
    """
    versions = {}
    for name in ('instagrapi', ):
        item = pkg_resources.require(name)
        if item:
            versions[name] = item[0].version
    return versions


@app.exception_handler(Exception)
async def handle_exception(request, exc: Exception):
    return JSONResponse({"detail": str(exc), "exc_type": str(type(exc).__name__)}, status_code=500)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    # for route in app.routes:
    #     body_field = getattr(route, 'body_field', None)
    #     if body_field:
    #         body_field.type_.__name__ = 'name'
    openapi_schema = get_openapi(
        title="instagrapi-rest",
        version="1.0.0",
        description="RESTful API Service for instagrapi",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
