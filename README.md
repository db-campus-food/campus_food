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

## 실제 데이터 넣는 방법 (엑셀 → DB)

1. `data/campus_menu.xlsx`를 열어 건물 → 관리자 → 매장 → 메뉴 시트 순서로 입력한다. (`안내` 시트에 규칙이 있음)
2. 변환: `python tools/excel_to_seed.py` → `sql/seed_real.sql`이 만들어진다. 엑셀에 오류가 있으면 몇 행이 문제인지 알려 준다.
3. Workbench에서 `sql/schema.sql` → `sql/seed_real.sql` 순서로 실행한다. (`seed.sql`은 가상 샘플용)

## 폴더 구조

```
sql/schema.sql   테이블 생성
sql/seed.sql     가상 샘플 데이터 (is_sample = TRUE)
sql/seed_real.sql  실제 데이터 (엑셀에서 자동 생성)
data/campus_menu.xlsx  데이터 입력 양식
tools/           엑셀 양식 생성·엑셀→SQL 변환 스크립트
db.py            MySQL 연결 및 SQL 함수
app.py           일반 사용자 화면 (streamlit run app.py)
```

`db_config.py`(비밀번호)와 `venv/`는 GitHub에 올리지 않습니다.
