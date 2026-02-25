from fastapi import Depends, HTTPException
from app.api.deps_auth import get_current_user
from app.models.models import User

def require_role(*roles: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep
