from typing import List, Optional
from pathlib import Path
import requests
import json
from pydantic import AnyHttpUrl
from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import FileResponse
from instagrapi.types import (
    Story, StoryHashtag, StoryLink,
    StoryLocation, StoryMention, StorySticker,
    Media, Location, Usertag
)
from helpers import photo_upload_story_as_video, photo_upload_story_as_photo, photo_upload_post
from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/photo",
    tags=["photo"],
    responses={404: {"description": "Not found"}},
)


@router.post("/upload_to_story", response_model=Story)
async def photo_upload_to_story(sessionid: str = Form(...),
                                file: UploadFile = File(...),
                                as_video: Optional[bool] = Form(False),
                                caption: Optional[str] = Form(""),
                                mentions: Optional[List[StoryMention]] = Form([]),
                                locations: Optional[List[StoryLocation]] = Form([]),
                                links: Optional[List[StoryLink]] = Form([]),
                                hashtags: Optional[List[StoryHashtag]] = Form([]),
                                stickers: Optional[List[StorySticker]] = Form([]),
                                clients: ClientStorage = Depends(get_clients)
                                ) -> Story:
    """Upload photo to story
    """
    cl = clients.get(sessionid)
    content = await file.read()
    if as_video:
        return await photo_upload_story_as_video(
            cl, content, caption=caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers)
    else:
        return await photo_upload_story_as_photo(
            cl, content, caption=caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers)


@router.post("/upload_to_story/by_url", response_model=Story)
async def photo_upload_to_story_by_url(sessionid: str = Form(...),
                                url: AnyHttpUrl = Form(...),
                                as_video: Optional[bool] = Form(False),
                                caption: Optional[str] = Form(""),
                                mentions: Optional[List[StoryMention]] = Form([]),
                                locations: Optional[List[StoryLocation]] = Form([]),
                                links: Optional[List[StoryLink]] = Form([]),
                                hashtags: Optional[List[StoryHashtag]] = Form([]),
                                stickers: Optional[List[StorySticker]] = Form([]),
                                clients: ClientStorage = Depends(get_clients)
                                ) -> Story:
    """Upload photo to story by URL to file
    """
    cl = clients.get(sessionid)
    content = requests.get(url).content
    if as_video:
        return await photo_upload_story_as_video(
            cl, content, caption=caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers)
    else:
        return await photo_upload_story_as_photo(
            cl, content, caption=caption,
            mentions=mentions,
            links=links,
            hashtags=hashtags,
            locations=locations,
            stickers=stickers)



@router.post("/download")
async def photo_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download photo using media pk
    """
    cl = clients.get(sessionid)
    result = cl.photo_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/download/by_url")
async def photo_download_by_url(sessionid: str = Form(...),
                         url: str = Form(...),
                         filename: Optional[str] = Form(""),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download photo using URL
    """
    cl = clients.get(sessionid)
    result = cl.photo_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/upload", response_model=Media)
async def photo_upload(sessionid: str = Form(...),
                       file: UploadFile = File(...),
                       caption: str = Form(...),
                       upload_id: Optional[str] = Form(""),
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
    return await photo_upload_post(
        cl, content, caption=caption,
        upload_id=upload_id,
        usertags=usernames_tags,
        location=location)

@router.post("/upload/by_url", response_model=Media)
async def photo_upload(sessionid: str = Form(...),
                       url: AnyHttpUrl = Form(...),
                       caption: str = Form(...),
                       upload_id: Optional[str] = Form(""),
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
        
    content = requests.get(url).content
    return await photo_upload_post(
        cl, content, caption=caption,
        upload_id=upload_id,
        usertags=usernames_tags,
        location=location)
