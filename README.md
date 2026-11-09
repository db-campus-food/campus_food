# 교내 음식점·카페 메뉴 통합 관리 및 추천 시스템

데이터베이스 팀 프로젝트 (Python + MySQL 8.0 + Streamlit)

## 처음 받았을 때 설정

1. Python 3.12 설치 (Add python.exe to PATH 체크)
2. 가상환경 만들고 패키지 설치
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. MySQL Workbench에서 `sql/schema.sql` → `sql/seed.sql` 순서로 실행
4. `db_config.example.py`를 복사해 `db_config.py`로 만들고 본인 MySQL 비밀번호 입력
5. 연결 테스트: `python db.py`

## 폴더 구조

```
sql/schema.sql   테이블 생성
sql/seed.sql     초기 데이터 (현재는 테스트용 가상 데이터)
db.py            MySQL 연결 및 SQL 함수
```

`db_config.py`(비밀번호)와 `venv/`는 GitHub에 올리지 않습니다.
