from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Session, relationship

from app.database.conn import Base, db


class BaseMixin:
    id = Column(Integer,
                primary_key=True,
                index=True)
    created_at = Column(DateTime,
                        nullable=False,
                        default=func.utc_timestamp()
                        )  # 생성시간
    updated_at = Column(DateTime,
                        nullable=False,
                        default=func.utc_timestamp(),
                        onupdate=func.utc_timestamp()
                        )  # 업데이트시간

    def __init__(self):
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return [col for col in self.__table__.columns if col.primary_key is False and col.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod  # cls : 클래스(BaseMixin)를 가리킴
    def create(cls, session: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()  # 내부에서 직접 instacing을 진행
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        print("session ", session)
        print("obj ", obj)
        session.add(obj)
        session.flush()
        if auto_commit:
            session.commit()
        return obj

    @classmethod
    def get(cls, session: Session = None, **kwargs):
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        sess = next(db.session()) if not session else session
        query = sess.query(cls)
        for key, val in kwargs.items():
            print("key, val", key, val)
            col = getattr(cls, key)
            query = query.filter(col == val)

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.")
        result = query.first()
        if not session:
            sess.close()
        return result


class Users(Base, BaseMixin):
    __tablename__ = "users"
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    name = Column(String(length=255), nullable=True)
    #phone_number = Column(String(length=20), nullable=True, unique=True)
    #profile_img = Column(String(length=1000), nullable=True)
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    #marketing_agree = Column(Boolean, nullable=True, default=True)
    #keys = relationship("ApiKeys", back_populates="users")
