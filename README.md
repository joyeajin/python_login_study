파이썬을 이용한 회원가입과 로그인 스터디,,,,

2024.06.28 17:03
로그인 로직
1. 회원 존재 여부 확인
2. 확인 후 비밀번호 비교 체크
3. 로그인 성공하면 access token 발급
4. refresh token도 발급.,,..했지만 fast api로 post하니까 오류발생
2024.07.01
5. refresh token 오류 수정(헤더 이름이 잘못됐었음)
6. access token 만료되면 refresh token 발급되도록 함수 추가