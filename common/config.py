from dataclasses import dataclass, asdict
from os import path, environ

# 중요 : base_dir/config.py 상위의 app 경로를 가리킴, config 파일 위치가 달라지면 base_dir 도 같이 체크 해줘야함
base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

user_name = "root"
user_pwd = "gksgywjddld10!"
db_host = "127.0.0.1"
db_name = "quant_on_test"

DATABASE = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
    user_name,
    user_pwd,
    db_host,
    db_name,
)


@dataclass  # dictionary 형태로 가져오기위해 dataclass 선언
class Config:
    """
    기본 Configuration
    """
    BASE_DIR : str = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True  # DB 실행시 echo 출력 여부
    DEBUG: bool = False
    TEST_MODE: bool = False
    DB_URL: str = environ.get("DB_URL", DATABASE)


@dataclass
class LocalConfig(Config):  # 로컬서버, Config 부모클래스 상속
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    DEBUG: bool = True


@dataclass
class ProdConfig(Config):  # 운영서버, Config 부모클래스 상속
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class TestConfig(Config):  # 테스트서버
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    TEST_MODE: bool = True


def conf():
    """
    환경 불러오기
    환경변수 API_ENV을 확인하고, 값이 없다면 local을 이용
    """
    config = dict(prod=ProdConfig, local=LocalConfig, test=TestConfig)
    return config[environ.get("API_ENV", "local")]()  # python 스위치함수가 없기 때문에 이렇게 이용

