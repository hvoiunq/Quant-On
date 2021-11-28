from typing import List
from uuid import uuid4

import bcrypt
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi.logger import logger

# from app.common.consts import MAX_API_KEY
from app.database.conn import db
# from app.database.schema import Users, ApiKeys
from app import models as m
from app.errors import exceptions as ex
import string
import secrets

from starlette.requests import Request

from app.database.schema import Users
from app.errors.exceptions import NotFoundUserEx
from app.models import UserMe
# from app.models import MessageOk

router = APIRouter(prefix='/user')


@router.get('/me')
async def get_me(request: Request):
    """
    .all() 전부
    .first() 첫번째 로우만
    .count() 갯수반환
     alchemy를 이용하는경우 ->
    """
    print("/user/me request ", request)
    user = request.state.user
    user_info = Users.get(id=user.id)
    user_info = Users.filter(id__gt=user.id).order_by("-email").count() # - : 내림차
    # 위와 동일한 쿼리 : user_info = session.query(Users).filter(Users.id > user.id).order_by(Users.email.asc()).count()
    # 전달받은 session 사용, 가볍게 한번만 수행하는 쿼리는 session을 가져올필요가 없을거같

    return user_info


@router.put('/me')
async def put_me(request: Request):
    ...


@router.delete('/me')
async def delete_me(request: Request):
    ...
