from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.requests import Request
from inspect import currentframe as frame

router = APIRouter()


@router.get("/")
async def index():
    """
    ELB 상태 체크용 API
    :param session:
    :return:
    """
    current_time = datetime.utcnow()
    return Response(f"Notifiction API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get("/test")
async def test(request: Request):
    """
    ELB 상태 체크용 API
    :return:
    """
    print("state.user ", request, request.state.user)
    # try:
    #     a = 1/0  # 테스트 -> 일부러 오류발생 테스트
    # except Exception as e:  # 핸들링되지 않을 에러가 있을때 사용하는
    #     request.state.inspect = frame()
    #     raise e
    current_time = datetime.utcnow()
    return Response(f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")