from datetime import datetime, timedelta

import bcrypt
import jwt  # json web token, 인증/access/refresh 등에 쓰인다
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session  # 타이핑을 위한..?
from starlette.responses import JSONResponse  # starlette JSON형태로 response해주는 모듈

from app import models
from app.common.consts import JWT_SECRET, JWT_ALGORITHM  # json web token은 키가있어야 decode가능 (내가준 token을 쓰고있는지 incode, decode를 하여 확인하는 보안용도)
from app.database.conn import db
from app.database.schema import Users
from app.models import SnsType, Token, UserToken, UserRegister

# TODO:
"""
1. 구글 로그인을 위한 구글 앱 준비 (구글 개발자 도구)
2. FB 로그인을 위한 FB 앱 준비 (FB 개발자 도구)
3. 카카오 로그인을 위한 카카오 앱준비( 카카오 개발자 도구)
4. 이메일, 비밀번호로 가입 (v)
5. 가입된 이메일, 비밀번호로 로그인, (v)
6. JWT 발급 (v)

7. 이메일 인증 실패시 이메일 변경 -> 메일서버 필요 
8. 이메일 인증 메일 발송
9. 각 SNS 에서 Unlink 
10. 회원 탈퇴
11. 탈퇴 회원 정보 저장 기간 동안 보유(법적 최대 한도 내에서, 가입 때 약관 동의 받아야 함, 재가입 방지 용도로 사용하면 가능)

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method not allowed
500 Internal Error
502 Bad Gateway 
504 Timeout
200 OK
201 Created

"""


router = APIRouter(prefix="/auth")


# router에 연결되어있는애만 async로 진행하면 됨
@router.post("/register/{sns_type}", status_code=201, response_model=Token)
async def register(sns_type: SnsType, reg_info: UserRegister, session: Session = Depends(db.session)):
    """
    회원가입 API\n
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    # 이메일 회원가입
    if sns_type == SnsType.email:  # 객체화 -> "email" 이렇게 비교해주는거보다 여러번 이용이 가능하고 구독성이 좋음
        is_exist = await is_email_exist(reg_info.email)  # 자주 쓰일거같은 모듈을 따로 util이나 component로 정의
        if not reg_info.email or not reg_info.pw:
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided'"))  # 없으면 400에러 -> JSON으로 명시적오류를 써줬지만 미들웨어 raise를 이용하게 될 것
        if is_exist:
            return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
        hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"), bcrypt.gensalt())  # bcrypt : 해쉬함수, pw 검증을 하는방식 -> 해쉬로 비교, gensalt로 유추할수없게끔 조금만 다른 input이면 값이 달라진다 + 해쉬는 byte코드만 가능-> utf-8 인코딩
        new_user = Users.create(session, auto_commit=True, pw=hash_pw, email=reg_info.email)  # Create를 클래스메소드로 변경했기 떄문에 Users().creat() -> Users.create(), hash된 pw를 넘겨줌
        token = dict(
                    Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'pw', ''}),)}"
                )  # token 생성, exlude : 제외 ,Authorization=f"Bearer 표준
        #print("t", token)
        return token
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


@router.post("/login/{sns_type}", status_code=200, response_model=Token)
async def login(sns_type: SnsType, user_info: models.UserRegister):
    if sns_type == SnsType.email:  # 이메일 로그인
        is_exist = await is_email_exist(user_info.email)  # await : async 함수와 같이 써줘야함

        if not user_info.email or not user_info.pw:
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided'"))
        if not is_exist:  # 이메일 미존재
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

        user = Users.get(email=user_info.email)
        is_verified = bcrypt.checkpw(user_info.pw.encode("utf-8"), user.pw.encode("utf-8"))

        if not is_verified:  # 비밀번호 불일치
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

        token = dict(
                Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw', 'marketing_agree'}), )}"
                )  # json web token 반환
        return token

    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


async def is_email_exist(email: str):  # end point 는 아니고, 자주쓰이는 함수라 별도 정의 -> async 일 필요가 없다
    get_email = Users.get(email=email)

    if get_email:
        return True
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()

    if expires_delta:  # ?
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt