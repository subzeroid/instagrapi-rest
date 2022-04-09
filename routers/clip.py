from typing import List, Optional
from pathlib import Path
import requests
import json
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, UploadFile, Form
from instagrapi.types import Media, Location, Usertag

from dependencies import ClientStorage, get_clients
from helpers import clip_upload_post


router = APIRouter(
    prefix="/clip",
    tags=["clip"],
    responses={404: {"description": "Not found"}},
)


@router.post("/download")
async def clip_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download CLIP video using media pk
    """
    cl = clients.get(sessionid)
    result = cl.clip_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/download/by_url")
async def clip_download_by_url(sessionid: str = Form(...),
                         url: str = Form(...),
                         filename: Optional[str] = Form(""),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download CLIP video using URL
    """
    cl = clients.get(sessionid)
    result = cl.clip_download_by_url(url, filename, folder)
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
    cl = clients.get(sessionid)
    
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

@router.post("/upload/by_url", response_model=Media)
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
    cl = clients.get(sessionid)
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
