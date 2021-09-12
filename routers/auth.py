import json
from typing import Optional, Dict
from fastapi import APIRouter, Depends, Form
from dependencies import ClientStorage, get_clients

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}}
)

@router.post("/login")
async def auth_login(username: str = Form(...),
                     password: str = Form(...),
                     verification_code: Optional[str] = Form(""),
                     clients: ClientStorage = Depends(get_clients)) -> str:
    """Login by username and password with 2FA
    """
    cl = clients.client()

    result = cl.login(
        username,
        password,
        verification_code=verification_code
    )
    if result:
        clients.set(cl)
        return cl.sessionid
    return result


@router.post("/relogin")
async def auth_relogin(sessionid: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)) -> str:
    """Relogin by username and password (with clean cookies)
    """
    cl = clients.get(sessionid)
    result = cl.relogin()
    return result


@router.get("/settings/get")
async def settings_get(sessionid: str,
                   clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get client's settings
    """
    cl = clients.get(sessionid)
    return cl.get_settings()


@router.post("/settings/set")
async def settings_set(settings: str = Form(...),
                       sessionid: Optional[str] = Form(""),
                       clients: ClientStorage = Depends(get_clients)) -> str:
    """Set client's settings
    """
    if sessionid != "":
        cl = clients.get(sessionid)
    else:
        cl = clients.client()
    cl.set_settings(json.loads(settings))
    cl.expose()
    clients.set(cl)
    return cl.sessionid

@router.get("/timeline_feed")
async def timeline_feed(sessionid: str,
                   clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get your timeline feed
    """
    cl = clients.get(sessionid)
    return cl.get_timeline_feed()
