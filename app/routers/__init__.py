from .accounts import router as accounts
from .auth import router as auth
from .platforms import router as platforms
from .users import router as users
from .web import router as web

__all__ = ["accounts", "auth", "platforms", "users", "web"] 