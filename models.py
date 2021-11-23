# 모든 데이터를 객체화시켜서 이용할 수 있도록 정의
from enum import Enum

from pydantic.main import BaseModel
from pydantic.networks import EmailStr


class UserRegister(BaseModel):
    # EamilStr사용을 위한 필수설치 -> pip install 'pydantic[email]'
    # 아래의 형태로 값이 들어오면 json형태로 변환해준다
    email: EmailStr = None
    pw: str = None


class SnsType(str, Enum):
    # income model
    # Enum : 아래중 하나만 들어올 수 있음    email: str = "email"  # 인터프린터 언어는 절대 빨라지는건 아니고, 보기좋은 용도
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class Token(BaseModel):
    # Response model : 나가는 json 모델, 이런 객체를 json으로 변환해 내보내겠다
    Authorization: str = None


class UserToken(BaseModel):
    id: int
    pw: str = None
    email: str = None
    name: str = None
    sns_type: str = None

    class Config:
        orm_mode = True

class UserMe(BaseModel):
    id: int
    sns_type: str = None

    class Config:
        orm_mode = True