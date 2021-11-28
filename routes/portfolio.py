from fastapi import APIRouter, Depends

from starlette.responses import Response
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database.conn import db
from app.database.schema import Users

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

router = APIRouter(prefix='/portfolio')


@router.get("/myPortfolio")
async def get_my_portfolio(request: Request, session: Session = Depends(db.session)):
    print("get Portfolio")

    user = request.state.user
    user_portfolio =
