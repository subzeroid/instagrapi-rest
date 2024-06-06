import json
from unittest.mock import patch
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
                     proxy: Optional[str] = Form(""),
                     locale: Optional[str] = Form(""),
                     timezone: Optional[str] = Form(""),
                     clients: ClientStorage = Depends(get_clients)) -> str:
    """Login by username and password with 2FA
    """
    cl = clients.client()
    if proxy != "":
        cl.set_proxy(proxy)

    if locale != "":
        cl.set_locale(locale)

    if timezone != "":
        cl.set_timezone_offset(timezone)

    # We're mocking the input
    with patch('builtins.input', return_value=verification_code):
        result = cl.login(username, password)

    if result:
        clients.set(cl)
        return cl.sessionid
    return result


@router.post("/login_by_sessionid")
async def auth_login_by_sessionid(sessionid: str = Form(...),
                                  clients: ClientStorage = Depends(get_clients)) -> str:
    """Login by sessionid
    """
    cl = clients.client()
    result = cl.login_by_sessionid(sessionid)
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
