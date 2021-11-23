from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import logging


# DB 관리는 싱글턴으로 관리되어야함
# 딱 한곳만 session을 유지할 수 있게 끔..!
class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._session = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        """
        DB 초기화 함수
        :param app: FastAPI 인스턴스
        :param kwargs:
        :return:
        """
        database_url = kwargs.get("DB_URL")  # config.py에 정의된 DB_URL
        pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)
        echo = kwargs.setdefault("DB_ECHO", True)  # 로깅 출력 여부

        # engine 생성
        self._engine = create_engine(
                            database_url,
                            echo=echo,
                            pool_recycle=pool_recycle,
                            pool_pre_ping=True,
                        )

        # seesion 생성 : SQLAlchemy 이용해 생성 (sessionmaker)
        self._session = sessionmaker(
                            autocommit=False,
                            autoflush=False,
                            bind=self._engine
                        )

        @app.on_event("startup")  # 앱이 실행될 때 가장먼저 실행되는 함수
        async def startup() -> None:
            """
            앱이 시작될 때 구성
            """
            self._engine.connect()
            logging.info("DB connected.")

        @app.on_event("shutdown")  # 앱이 종료될 때 실행되는 함수
        async def shutdown() -> None:
            """
            앱이 종료될 때 구성
            """
            self._session.close_all()  # session 종료
            self._engine.dispose()  # engine 종료
            logging.info("DB disconnected")  # logging

    def get_db(self):
        """
        요청마다 DB 세션 유지 함수
        :return:
        """
        if self._session is None:
            raise Exception("must be called 'init_app'")
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()

    @property
    def session(self):
        return self.get_db  # session 가져오기

    @property
    def engine(self):
        return self._engine


db = SQLAlchemy()
Base = declarative_base()