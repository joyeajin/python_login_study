## 파이썬을 이용한 회원가입과 로그인 스터디,,,,

### 2024.06.28 17:03
(로그인 로직)

- 회원 존재 여부 확인

- 확인 후 비밀번호 비교 체크

- 로그인 성공하면 access token 발급

- refresh token도 발급.,,..했지만 fast api로 post하니까 오류발생
---
### 2024.07.01
- refresh token 오류 수정(헤더 이름이 잘못됐었음)

- access token 만료되면 refresh token 발급되도록 함수 추가
---
### 2024.07.02
- Token스키마에 member테이블 추가

- 실제 test db에 연결 (거의 세시간을 씨름했다...)
    - db url을 전부 넣었어야 함
    - serverTimezone이랑 characterEncoding은 파이썬의 sqlalchemy에서 읽지못해서 sqlalchemy가 읽을 수 있게 수정해서 넣음
    - get_app_member_by_user_id 함수에서 filter 할 때 .first()로 했어야 하는데 .all()로 돼있어서 데이터를 제대로 못뽑아왔었음

- 로그인 할 때 access_token 쿠키에 저장
---
### 2024.07.03
- Token 스키마에 expiredIn(access token 만료시간) 추가

- is_delete 이용해 탈퇴한 회원 여부 체크

- response body에 code 추가

- create_access_token, create_refresh_token로 나뉘어있던 함수를 create_token 하나로 합치고 인자로 token_type 받도록 리팩토링

- 로그아웃 JSONResponse로 수정