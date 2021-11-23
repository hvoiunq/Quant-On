from fastapi import APIRouter
from starlette.requests import Request

from app.database.schema import Users
from app.errors.exceptions import NotFoundUserEx
from app.models import UserMe

router = APIRouter()


@router.get("/me", response_model=UserMe)  # response_model을 따로 지정해주지 않으면 객체의 모든 값이 출력됨
async def get_user(request: Request):
    """
    get my info
    :param request:
    :return:
    """
    # middelware에서 반환해준 값을 그대로 이용가능
    user = request.state.user  # 객체이용
    # before : user["id"]
    user_info = Users.get(id=user.id)
    return user_info  # 객체이지만 json 형태로 반환해주는
