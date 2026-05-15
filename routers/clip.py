import json
from pathlib import Path
from typing import List, Optional

import requests
from aiograpi.types import Location, Media, Usertag
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse

from dependencies import ClientStorage, get_clients
from helpers import clip_upload_post

router = APIRouter(
    prefix="/clip",
    tags=["clip"],
    responses={404: {"description": "Not found"}},
)


@router.get("/download")
async def clip_download(sessionid: str = Query(...),
                         media_pk: int = Query(...),
                         folder: Optional[Path] = Query(""),
                         returnFile: Optional[bool] = Query(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download CLIP video using media pk
    """
    cl = await clients.get(sessionid)
    result = await cl.clip_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.get("/download/by/url")
async def clip_download_by_url(sessionid: str = Query(...),
                         url: str = Query(...),
                         filename: Optional[str] = Query(""),
                         folder: Optional[Path] = Query(""),
                         returnFile: Optional[bool] = Query(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download CLIP video using URL
    """
    cl = await clients.get(sessionid)
    result = await cl.clip_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/upload", response_model=Media)
async def clip_upload(sessionid: str = Form(...),
                       file: UploadFile = File(...),
                       caption: str = Form(...),
                       thumbnail: Optional[UploadFile] = File(None),
                       usertags: Optional[List[str]] = Form([]),
                       location: Optional[Location] = Form(None),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload photo and configure to feed
    """
    cl = await clients.get(sessionid)

    usernames_tags = []
    for usertag in usertags:
        usertag_json = json.loads(usertag)
        usernames_tags.append(Usertag(user=usertag_json['user'], x=usertag_json['x'], y=usertag_json['y']))

    content = await file.read()
    if thumbnail is not None:
        thumb = await thumbnail.read()
        return await clip_upload_post(
            cl, content, caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=location)
    return await clip_upload_post(
            cl, content, caption=caption,
            usertags=usernames_tags,
            location=location)

@router.post("/upload/by/url", response_model=Media)
async def clip_upload(sessionid: str = Form(...),
                       url: str = Form(...),
                       caption: str = Form(...),
                       thumbnail: Optional[UploadFile] = File(None),
                       usertags: Optional[List[str]] = Form([]),
                       location: Optional[Location] = Form(None),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload photo by URL and configure to feed
    """
    cl = await clients.get(sessionid)
    usernames_tags = []
    for usertag in usertags:
        usertag_json = json.loads(usertag)
        usernames_tags.append(Usertag(user=usertag_json['user'], x=usertag_json['x'], y=usertag_json['y']))

    content = requests.get(url).content
    if thumbnail is not None:
        thumb = await thumbnail.read()
        return await clip_upload_post(
            cl, content, caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=location)
    return await clip_upload_post(
            cl, content, caption=caption,
            usertags=usernames_tags,
            location=location)
