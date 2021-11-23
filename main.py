# import declaration
from dataclasses import asdict
from pydantic import BaseModel
from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware  # ?
from starlette.middleware.cors import CORSMiddleware

from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.database.conn import db
from app.common.config import conf
from app.middleware.token_validator import access_control
from app.middleware.trusted_hosts import TrustedHostMiddleware
from app.routes import index, auth, users


API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)  # docs내에 authorization 버튼 생성, auto_error :


def create_app():
    """
    앱 함수 실행
    초기화
    """
    con = conf()  # 환경변수에 따라 config 성질 가져와 con에 저장
    app = FastAPI(title="quant-on", version="1")

    # 데이터 베이스 이니셜라이즈
    conf_dict = asdict(con)  # Config 자체는 객체라서 dictionary 형태가 되지 않아 asdict함수 같이 사용
    db.init_app(app, **conf_dict)  # dictionary 형태의 config 결과를 db.init에 전달
    print(conf_dict)

    # 레디스 이니셜라이즈

    # 미들웨어 정의
    # 실행 순서 (스택구조) -> 3, 2, 1 라인 미들웨어순으로 실행됨
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(  # 이게 명시되어 있지 않으면 백엔드, 프론트엔드의 도메인주소가 무조건 같아야만 응답을 받을 수 있게 된다 (삽질포인트)
            CORSMiddleware,
            allow_origins=conf().ALLOW_SITE,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=conf().TRUSTED_HOSTS,
            except_path=["/health"]
        )

    # 라우터 정의
    app.include_router(index.router)  # app 이 실행될때 라우터가 있다고 알리는 선언
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")  # auth에 해당하는 router 생성, prefix : 디폴트 경로이름 설정
    app.include_router(users.router, tags=["Users"], prefix="/api", dependencies=[Depends(API_KEY_HEADER)])  # Dependency가 걸린 api는 모두 자물쇠모양이 생성 -> key입력없이는 접근 불가, 토큰검사를 해주는 역

    return app

app = create_app()

# 다른 모듈에서 실행되는 경우 파일명 달라짐, main.py에서 실행되는 경우에만 실행, 실제 운영에서는 이렇게 실행시키지 않음, reload=conf().PROJ_RELOAD -> 로컬에서 수행되므로 True
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
