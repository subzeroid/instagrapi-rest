from typing import List, Optional
from pathlib import Path
import requests
import json
from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import FileResponse
from instagrapi.types import Media, Location, Usertag

from dependencies import ClientStorage, get_clients
from helpers import igtv_upload_post

router = APIRouter(
    prefix="/igtv",
    tags=["igtv"],
    responses={404: {"description": "Not found"}},
)


@router.post("/download")
async def igtv_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download IGTV video using media pk
    """
    cl = clients.get(sessionid)
    result = cl.igtv_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/download/by_url")
async def igtv_download_by_url(sessionid: str = Form(...),
                         url: str = Form(...),
                         filename: Optional[str] = Form(""),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download IGTV video using URL
    """
    cl = clients.get(sessionid)
    result = cl.igtv_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/upload", response_model=Media)
async def igtv_upload(sessionid: str = Form(...),
                       file: UploadFile = File(...),
                       title: str = Form(...),
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
        return await igtv_upload_post(
            cl, content, title=title,
            caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=location)
    return await igtv_upload_post(
        cl, content, title=title,
        caption=caption,
        usertags=usernames_tags,
        location=location)
    
@router.post("/upload/by_url", response_model=Media)
async def igtv_upload(sessionid: str = Form(...),
                       url: str = Form(...),
                       title: str = Form(...),
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
        return await igtv_upload_post(
            cl, content, title=title,
            caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=location)
    return await igtv_upload_post(
        cl, content, title=title,
        caption=caption,
        usertags=usernames_tags,
        location=location)
