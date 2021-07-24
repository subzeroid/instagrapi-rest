from typing import List, Optional

import requests
from pydantic import HttpUrl
from fastapi import APIRouter, Depends, File, UploadFile, Form
from instagrapi.types import (
    Story, StoryHashtag, StoryLink,
    StoryLocation, StoryMention, StorySticker
)

from helpers import photo_upload_story_as_video, photo_upload_story_as_photo
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
                                url: HttpUrl = Form(...),
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
