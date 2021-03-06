# 들어오는 모든 token 에 대해 체크하는 모듈
import time
import typing
import re
import jwt  # db를 거치지 않고 유저의 로그인정보를 가지고 있을 수 있
import sqlalchemy.exc

from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX

from app.common import config, consts
from app.models import UserToken
from app.errors import exceptions as ex
from app.errors.exceptions import APIException, SqlFailureEx

from app.utils.date_utils import D

from app.utils.logger import api_logger


async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None

    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    request.state.ip = ip.split(",")[0] if "," in ip else ip  # 부가정보 삭제
    headers = request.headers
    cookies = request.cookies

    url = request.url.path

    # 토큰검사 생략 URL
    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        if url != "/":
            await api_logger(request=request, response=response)
        return response

    try:
        if url.startswith("/api"):
            # api 인경우 헤더로 토큰 검사
            print("api ", headers.keys())
            if "authorization" in headers.keys():
                token_info = await token_decode(access_token=headers.get("Authorization"))
                request.state.user = UserToken(**token_info)
                # 토큰 없음

            else:
                if "authorization" not in headers.keys():
                    raise ex.NotAuthorized()

        else:
            # 템플릿 렌더링인 경우 쿠키에서 토큰 검사
            request.cookies[
                "Authorization"] = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6OCwiZW1haWwiOiJ0ZXN0MkBleGFtcGxlLmNvbSIsIm5hbWUiOm51bGwsInNuc190eXBlIjpudWxsfQ.uwAzuGCkifFvici4ow_Hjj7Ac7Gcx2GP8DJ8pD6ZAxE'

            if "Authorization" not in cookies.keys():
                raise ex.NotAuthorized()

            token_info = await token_decode(access_token=cookies.get("Authorization"))
            request.state.user = UserToken(**token_info)
            # end TOKEN 검사

        response = await call_next(request)  # end-point 함수 실행(API), end-point 의 return을 기다림
        await api_logger(request=request, response=response)

    except Exception as e:

        error = await exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)

    return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[consts.JWT_ALGORITHM])
        # print("token payload ", payload)
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload


async def exception_handler(error: Exception):
    if isinstance(error, sqlalchemy.exc.OperationalError):
        error = SqlFailureEx(ex=error)
    if not isinstance(error, APIException):
        error = APIException(ex=error, detail=str(error))  # exception을 APIException 방식으로 변경
    return error