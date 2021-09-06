from fastapi import APIRouter, Depends, Form

from typing import List, Dict, Optional

from instagrapi import Client
from instagrapi.mixins.insights import POST_TYPE, TIME_FRAME, DATA_ORDERING

from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/insights",
    tags=["insights"],
    responses={404: {"description": "Not found"}}
)


@router.post("/media_feed_all", response_model=List[Dict])
async def media_feed_all(sessionid: str = Form(...),
                         post_type: POST_TYPE = "ALL",
                         time_frame: TIME_FRAME = "TWO_YEARS",
                         data_ordering: DATA_ORDERING = "REACH_COUNT",
                         count: int = 0,
                         clients: ClientStorage = Depends(get_clients)) -> List[Dict]:
    """Return medias with insights
    """
    cl = clients.get(sessionid)
    return cl.insights_media_feed_all(post_type, time_frame, data_ordering, count, sleep=2)


@router.post("/account", response_model=Dict)
async def account(sessionid: str = Form(...),
                  clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get insights for account
    """
    cl = clients.get(sessionid)
    return cl.insights_account()


@router.post("/media", response_model=Dict)
async def media(sessionid: str = Form(...),
                media_pk: int = Form(...),
                clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get insights data for media
    """
    cl = clients.get(sessionid)
    return cl.insights_media(media_pk)
