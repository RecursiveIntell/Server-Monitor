from fastapi import APIRouter, Depends

from recursiveops.api.deps import get_current_user, get_settings
from recursiveops.settings import public_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")

def read_settings(settings=Depends(get_settings), _user=Depends(get_current_user)):
    return public_settings(settings)
