"""MySQL 연결과 SQL 실행을 담당하는 모듈.

화면(app.py, pages/admin.py)에서는 SQL을 직접 쓰지 않고 이 파일의 함수만 호출합니다.
"""
import pymysql

from db_config import DB_CONFIG


def get_connection():
    return pymysql.connect(
        **DB_CONFIG,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def fetch_all(sql, params=None):
    """SELECT 실행 → 결과를 딕셔너리 리스트로 반환."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def execute(sql, params=None):
    """INSERT / UPDATE / DELETE 실행 → 영향받은 행 수 반환."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            count = cur.execute(sql, params)
        conn.commit()
        return count


# ---------------- 일반 사용자 기능 ----------------

def get_categories():
    return fetch_all("SELECT category_id, category_name FROM category ORDER BY category_id")


def search_menus(keyword="", max_price=None, category=None, order="asc"):
    """메뉴 검색 + 예산 + 카테고리 + 가격 정렬 (기능 2·3·4)."""
    sql = """
        SELECT s.store_name   AS 매장명,
               m.menu_name    AS 메뉴명,
               m.price        AS 가격,
               c.category_name AS 종류,
               s.store_type   AS 매장유형,
               b.building_name AS 건물,
               s.location_info AS 위치
        FROM menu m
        JOIN store s    ON m.store_id = s.store_id
        JOIN building b ON s.building_id = b.building_id
        JOIN category c ON m.category_id = c.category_id
        WHERE m.is_available = TRUE
    """
    params = []
    if keyword:
        sql += " AND (m.menu_name LIKE %s OR s.store_name LIKE %s)"
        params += [f"%{keyword}%", f"%{keyword}%"]
    if max_price:
        sql += " AND m.price <= %s"
        params.append(max_price)
    if category and category != "전체":
        sql += " AND c.category_name = %s"
        params.append(category)
    sql += " ORDER BY m.price " + ("DESC" if order == "desc" else "ASC")
    return fetch_all(sql, params)


if __name__ == "__main__":
    # 연결 테스트: python db.py
    rows = search_menus(max_price=7000, category="한식")
    print(f"7,000원 이하 한식 메뉴 {len(rows)}개")
    for r in rows:
        print(r)
