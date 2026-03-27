import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from julca_bakalarka.settings import settings

security = HTTPBasic()


def verify_admin(
    credentials: HTTPBasicCredentials = Depends(security),
) -> None:
    """Verify admin credentials using HTTP Basic Auth."""
    correct_password = secrets.compare_digest(
        credentials.password,
        settings.admin_password,
    )
    correct_username = secrets.compare_digest(
        credentials.username,
        "admin",
    )
    if not (correct_password and correct_username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nesprávné přihlašovací údaje",
            headers={"WWW-Authenticate": "Basic"},
        )
