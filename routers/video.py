from typing import List, Optional
from pathlib import Path
import requests
import json
from pydantic import AnyHttpUrl
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, UploadFile, Form
from instagrapi.types import (
    Story, StoryHashtag, StoryLink,
    StoryLocation, StoryMention, StorySticker,
    Media, Usertag, Location
)

from helpers import video_upload_story, video_upload_post
from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)


@router.post("/upload_to_story", response_model=Story)
async def video_upload_to_story(sessionid: str = Form(...),
                                file: UploadFile = File(...),
                                caption: Optional[str] = Form(''),
                                mentions: List[StoryMention] = [],
                                locations: List[StoryLocation] = [],
                                links: List[StoryLink] = [],
                                hashtags: List[StoryHashtag] = [],
                                stickers: List[StorySticker] = [],
                                clients: ClientStorage = Depends(get_clients)
                                ) -> Story:
    """Upload video to story
    """
    cl = clients.get(sessionid)
    content = await file.read()
    return await video_upload_story(
        cl, content, caption=caption,
        mentions=mentions,
        links=links,
        hashtags=hashtags,
        locations=locations,
        stickers=stickers
    )


@router.post("/upload_to_story/by_url", response_model=Story)
async def video_upload_to_story_by_url(sessionid: str = Form(...),
                                       url: AnyHttpUrl = Form(...),
                                       caption: Optional[str] = Form(''),
                                       mentions: List[StoryMention] = [],
                                       locations: List[StoryLocation] = [],
                                       links: List[StoryLink] = [],
                                       hashtags: List[StoryHashtag] = [],
                                       stickers: List[StorySticker] = [],
                                       clients: ClientStorage = Depends(get_clients)
                                       ) -> Story:
    """Upload video to story by URL to file
    """
    cl = clients.get(sessionid)
    content = requests.get(url).content
    return await video_upload_story(
        cl, content, caption=caption,
        mentions=mentions,
        links=links,
        hashtags=hashtags,
        locations=locations,
        stickers=stickers
    )


@router.post("/download")
async def video_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download video using media pk
    """
    cl = clients.get(sessionid)
    result = cl.video_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/download/by_url")
async def video_download_by_url(sessionid: str = Form(...),
                         url: str = Form(...),
                         filename: Optional[str] = Form(""),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download video using URL
    """
    cl = clients.get(sessionid)
    result = cl.video_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/upload", response_model=Media)
async def video_upload(sessionid: str = Form(...),
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
        return await video_upload_post(
            cl, content, caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=location)
    return await video_upload_post(
        cl, content, caption=caption,
        usertags=usernames_tags,
        location=location)

@router.post("/upload/by_url", response_model=Media)
async def video_upload(sessionid: str = Form(...),
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
        return await video_upload_post(
            cl, content, caption=caption,
            thumbnail=thumb,
            usertags=usernames_tags,
            location=location)
    return await video_upload_post(
        cl, content, caption=caption,
        usertags=usernames_tags,
        location=location)
