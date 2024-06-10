from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, HTTPDigest

from tortoise.exceptions import DoesNotExist, OperationalError

from webweaver.auth.exceptions import UserInvalid, UserValidKeyInvalid
from webweaver.auth.models import User
from webweaver.auth.auth_module_base import AuthModuleBase



class HmacAuthModule(AuthModuleBase):
    pass