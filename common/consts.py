# 상수 정의 모듈
JWT_SECRET = "ABCD1234!"
JWT_ALGORITHM = "HS256"
EXCEPT_PATH_LIST = ["/", "/openapi.json"]  # docs, redoc이 문서를 만들때 openapi 문서를 가지고 오기 때문에 제, / : endpoint (헬스패스 체크용도)
EXCEPT_PATH_REGEX = "^(/docs|/redoc|/api/auth)"  # regular expression, 나열된 패쓰 모두 예외처리 , auth : 인증하는
#MAX_API_KEY = 3
#MAX_API_WHITELIST = 10