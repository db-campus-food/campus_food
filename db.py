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
    """카테고리 목록 (기능 4의 선택지)."""
    return fetch_all("SELECT category_id, category_name FROM category ORDER BY category_id")


def get_stores():
    """교내 매장 목록 + 건물·위치·판매 중 메뉴 수 (기능 1)."""
    sql = """
        SELECT s.store_id, s.store_name, s.store_type,
               b.building_name, s.location_info, s.is_sample,
               COUNT(m.menu_id) AS menu_count
        FROM store s
        JOIN building b ON s.building_id = b.building_id
        LEFT JOIN menu m ON m.store_id = s.store_id AND m.is_available = TRUE
        GROUP BY s.store_id, s.store_name, s.store_type,
                 b.building_name, s.location_info, s.is_sample
        ORDER BY b.building_name, s.store_name
    """
    return fetch_all(sql)


def search_menus(keyword="", max_price=None, category=None, order="asc"):
    """메뉴 검색 + 예산 + 카테고리 + 가격 정렬 (기능 2·3·4).

    keyword   : 메뉴명 또는 매장명에 포함된 글자 ("" 이면 조건 없음)
    max_price : 최대 예산 (None 이면 조건 없음)
    category  : 카테고리명 (None 또는 "전체" 이면 조건 없음)
    order     : "asc" 가격 낮은 순 / "desc" 가격 높은 순
    """
    sql = """
        SELECT m.menu_id, m.menu_name, m.price, c.category_name,
               s.store_name, s.store_type, b.building_name, s.location_info,
               (m.is_sample OR s.is_sample) AS is_sample
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
    sql += " ORDER BY m.price " + ("DESC" if order == "desc" else "ASC") + ", m.menu_name"
    return fetch_all(sql, params)


if __name__ == "__main__":
    # 연결 테스트: python db.py
    rows = search_menus(max_price=7000, category="한식")
    print(f"7,000원 이하 한식 메뉴 {len(rows)}개")
    for r in rows:
        print(f"  {r['store_name']} | {r['menu_name']} | {r['price']:,}원")
