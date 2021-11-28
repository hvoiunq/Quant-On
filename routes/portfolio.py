from fastapi import APIRouter

from starlette.responses import Response
from starlette.requests import Request

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
