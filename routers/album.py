from typing import List, Optional
from pathlib import Path
import json

from fastapi import APIRouter, Depends, File, UploadFile, Form
from instagrapi.types import Media, Location, Usertag

from dependencies import ClientStorage, get_clients
from helpers import album_upload_post


router = APIRouter(
    prefix="/album",
    tags=["album"],
    responses={404: {"description": "Not found"}},
)


@router.post("/download", response_model=List[Path])
async def album_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         clients: ClientStorage = Depends(get_clients)) -> List[Path]:
    """Download photo using media pk
    """
    cl = clients.get(sessionid)
    result = cl.album_download(media_pk, folder)
    return result


@router.post("/download/by_urls", response_model=List[Path])
async def album_download_by_urls(sessionid: str = Form(...),
                         urls: List[str] = Form(...),
                         folder: Optional[Path] = Form(""),
                         clients: ClientStorage = Depends(get_clients)) -> List[Path]:
    """Download photo using URL
    """
    cl = clients.get(sessionid)
    result = cl.album_download_by_urls(urls, folder)
    return result


@router.post("/upload", response_model=Media)
async def album_upload(sessionid: str = Form(...),
                       files: List[UploadFile] = File(...),
                       caption: str = Form(...),
                       usertags: Optional[List[str]] = Form([]),
                       location: Optional[Location] = Form(None),
                       clients: ClientStorage = Depends(get_clients)
                       ) -> Media:
    """Upload album to feed
    """
    cl = clients.get(sessionid)
    
    usernames_tags = []
    for usertag in usertags:
        usertag_json = json.loads(usertag)
        usernames_tags.append(Usertag(user=usertag_json['user'], x=usertag_json['x'], y=usertag_json['y']))
        
    return await album_upload_post(
        cl, files, caption=caption,
        usertags=usernames_tags,
        location=location)
