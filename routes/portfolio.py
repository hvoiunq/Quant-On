from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse  # html response를 할 수 있도록 도와주는 모듈
from fastapi.templating import Jinja2Templates

from starlette.responses import Response
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import models
from app.database.conn import db
from app.database.schema import Users, PortFolioManagement

# TODO:
"""
Quant-on main page
주요기능
 1. 포트폴리오 추가
    - 이름설
 2. 포트폴리오 종목 추가
 3. 현재 포트폴리오 상세 조회
    - 총자산 (현금 / 주식)
    - 수익률 (총 손익 / 총 매입)
    - YTD
    - MDD
    - CAGR
    - Sharp Ratio
 4. 포트폴리오 조회
    - 통화 선택
    - 정렬
    - 필터기능
"""

router = APIRouter(prefix='/portfolios')
template = Jinja2Templates(directory='templates')  # directory정의

@router.get("/main")
async def get_my_portfolio(request: Request,  session: Session = Depends(db.session)):
    """
    대표 포트폴리오 조회 API (main으로 설정된 포트폴리오를 조회한다)
    :param request:
    :param session:
    :return:
    """
    user = request.state.user
    user_portfolio = PortFolioManagement.filter(id__gt=user.id).order_by("-email").count()

    return user
    # return templates.TemplateResponse(, my_portfolio)  # 연결할 html 입력


@router.post("/{portfolio_id}")
async def create_portfolio(request: Request, session: Session = Depends(db.session)):
    """
    포트폴리오 생성 API
    :param request:
    :param session:
    :return:
    """
    user = request.state.user





@router.put("/")
async def update_portfolio(request: Request, session: Session = Depends(db.session)):
    """
    포트폴리오 수정 API
    :param request:
    :param session:
    :return:
    """


@router.get("/details/{portfolio_id}")
async def get_portfolio_details(portfolio_id : int, request: Request, session: Session = Depends(db.session)):
    """
    포트폴리오 상세 조회 API
    :param request:
    :param session:
    :return:
    """


@router.post("/details/{portfolio_id}")
async def get_portfolio_details(request: Request, session: Session = Depends(db.session)):
    """
    포트폴리오 수정, 삭제
    :param request:
    :param session:
    :return:
    """
