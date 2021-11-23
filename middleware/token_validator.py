# 들어오는 모든 token 에 대해 체크하는 모듈
import time
import typing
import re
import jwt  # db를 거치지 않고 유저의 로그인정보를 가지고 있을 수 있

from fastapi.params import Header
from jwt.exceptions import ExpiredSignatureError, DecodeError
from pydantic import BaseModel
from starlette.requests import Request
from starlette.datastructures import URL, Headers
from starlette.responses import JSONResponse, Response

from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.common import config, consts
from app.common.config import conf
from app.models import UserToken
from app.errors import exceptions as ex
from app.errors.exceptions import APIException

from app.utils.date_utils import D


class AccessControl:
    def __init__(
            self,
            app: ASGIApp,
            except_path_list: typing.Sequence[str] = None,
            except_path_regex: str = None,
    ) -> None:
        if except_path_list is None:
            except_path_list = ["*"]
        self.app = app
        self.except_path_list = except_path_list
        self.except_path_regex = except_path_regex

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # 실제 동작함수
        request = Request(scope=scope)
        headers = Headers(scope=scope)

        """
        request.state.user -> 새로 유저정보를 조회해야하면 function level(End api 레벨)에서 다시 조회하는게 좋다 (JWT 쓰는 이유)
        """
        request.state.start = time.time()  # 수행시간을 계산
        request.state.inspect = None  # 오류를 잡아주는(500에러), 그외에 내가 명시한 에러까지 잡아줌
        request.state.user = None  # 토큰을 디코드한 내용을 유저에 넣음
        request.state.is_admin_access = None

        ip_from = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else None  # request 헤드 체크

        if await self.url_pattern_check(request.url.path, self.except_path_regex) or request.url.path in self.except_path_list:
            return await self.app(scope, receive, send)

        try:
            if request.url.path.startswith("/api"):
                # api 인 경우 헤더로 토큰 검사
                print("request.headers.keys()", request.headers.keys())
                if "authorization" in request.headers.keys():
                    print("request.headers.get("'Authorization'") ", request.headers.get("Authorization"))
                    token_info = await self.token_decode(access_token=request.headers.get("Authorization"))
                    request.state.user = UserToken(**token_info)  # 객체화 , dictionary 형태가아닌 객체로 들어가는 형태
                    # 토큰 없음
                else:
                    if "authorization" not in request.headers.keys():
                        raise ex.NotAuthorized()
            else:
                # 템플릿 렌더링인 경우 쿠키에서 토큰 검사
                request.cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZW1haWwiOiJoeW9qdW5nQHRlc3QuY29tIiwibmFtZSI6bnVsbCwic25zX3R5cGUiOm51bGx9.K5UkNtHt8ORNaOaZfhbb6zOqb_3q-6er860jup4J6QY"

                if "Authorization" not in request.cookies.keys():
                    raise ex.NotAuthorized()

                token_info = await self.token_decode(access_token=request.cookies.get("Authorization"))
                request.state.user = UserToken(**token_info)

            request.state.req_time = D.datetime()  # request.state.변수명은 자유롭게 가능 -> 명시한 변수를 endpoint 에서도 이용가능하게 해준다
            print(D.datetime())
            print(D.date())
            print(D.date_num())

            print("request.cookies ", request.cookies)
            print("headers : ", headers)
            res = await self.app(scope, receive, send)

        except APIException as e:
            res = await self.exception_handler(e)
            res = await res(scope, receive, send)

        finally:
            # Logging
            ...

        return res

    @staticmethod
    async def url_pattern_check(path, pattern):  # 토큰검사 예외 url 체크
        result = re.match(pattern, path)
        if result:
            return True
        return False

    @staticmethod
    async def token_decode(access_token):
        """
        :param access_token:
        :return:
        """
        try:
            access_token = access_token.replace("Bearer ", "")
            payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[consts.JWT_ALGORITHM])
        except ExpiredSignatureError:
            raise ex.TokenExpiredEx()  # custom 에러로 변경
        except DecodeError:
            raise ex.TokenDecodeEx()
        return payload

    @staticmethod
    async def exception_handler(error: APIException):
        error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)  # 에러를 dictionary 형태로
        res = JSONResponse(status_code=error.status_code, content=error_dict)  # json 형태로 출력
        return res
