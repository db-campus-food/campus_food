"""관리자 기능용 SQL 함수 (팀원 A 담당).

db.py 의 연결 함수를 가져다 쓰며, 화면 파일(pages/2_관리자.py)에서는 SQL을 직접 쓰지 않는다.

권한 규칙: 관리자는 '자기가 담당하는 매장'(store.admin_id = 로그인한 관리자)의
메뉴·매장만 보고 수정할 수 있다. 모든 수정·삭제 SQL 에 이 조건이 들어 있다.

수정·삭제·등록 함수는 (성공 여부, 안내 문구) 를 돌려준다.
"""
import bcrypt
import pymysql

from db import fetch_all, get_connection

STORE_TYPES = ["학생식당", "일반음식점", "카페"]


def _friendly_error(e):
    """MySQL 오류를 화면에 보여줄 쉬운 문장으로 바꾼다."""
    code = e.args[0] if e.args else None
    if code == 1062:
        return "이미 같은 이름이 있습니다. (같은 매장에는 같은 메뉴명을 두 번 등록할 수 없습니다)"
    if code in (1264, 3819, 4025):
        return "입력한 값이 허용 범위를 벗어났습니다. 가격은 0 이상이어야 합니다."
    if code == 1452:
        return "존재하지 않는 매장·건물·카테고리를 선택했습니다."
    if code == 1451:
        return "다른 데이터가 사용 중이라 삭제할 수 없습니다."
    return f"데이터베이스 오류가 발생했습니다. ({e})"


# ---------------- 로그인 ----------------

def login(login_id, password):
    """아이디·비밀번호 확인. 성공하면 {'admin_id', 'admin_name'}, 실패하면 None."""
    rows = fetch_all(
        "SELECT admin_id, admin_name, password_hash FROM admin WHERE login_id = %s",
        (login_id,),
    )
    if not rows:
        return None
    row = rows[0]
    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8"))
    except ValueError:  # 해시 형식이 올바르지 않은 경우
        ok = False
    if not ok:
        return None
    return {"admin_id": row["admin_id"], "admin_name": row["admin_name"]}


# ---------------- 조회 (내 매장 것만) ----------------

def get_buildings():
    return fetch_all("SELECT building_id, building_name FROM building ORDER BY building_id")


def get_my_stores(admin_id):
    """내가 담당하는 매장 목록 + 메뉴 수."""
    sql = """
        SELECT s.store_id, s.store_name, s.store_type, s.location_info, s.is_sample,
               b.building_id, b.building_name, COUNT(m.menu_id) AS menu_count
        FROM store s
        JOIN building b ON s.building_id = b.building_id
        LEFT JOIN menu m ON m.store_id = s.store_id
        WHERE s.admin_id = %s
        GROUP BY s.store_id, s.store_name, s.store_type, s.location_info, s.is_sample,
                 b.building_id, b.building_name
        ORDER BY s.store_id
    """
    return fetch_all(sql, (admin_id,))


def get_my_menus(admin_id, store_id=None):
    """내 매장의 메뉴 목록 (판매 중지 메뉴도 포함)."""
    sql = """
        SELECT m.menu_id, m.menu_name, m.price, m.is_available, m.is_sample, m.updated_at,
               c.category_id, c.category_name, s.store_id, s.store_name
        FROM menu m
        JOIN store s    ON m.store_id = s.store_id
        JOIN category c ON m.category_id = c.category_id
        WHERE s.admin_id = %s
    """
    params = [admin_id]
    if store_id:
        sql += " AND s.store_id = %s"
        params.append(store_id)
    sql += " ORDER BY s.store_id, m.menu_id"
    return fetch_all(sql, params)


# ---------------- 메뉴 등록·수정·삭제 ----------------

def _owns_menu(cur, admin_id, menu_id):
    cur.execute(
        "SELECT 1 FROM menu m JOIN store s ON m.store_id = s.store_id "
        "WHERE m.menu_id = %s AND s.admin_id = %s",
        (menu_id, admin_id),
    )
    return cur.fetchone() is not None


def update_menu(admin_id, menu_id, price, is_available):
    """메뉴 가격·판매 여부 수정 (기능 5: 가격 변경, 판매 여부 변경)."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if not _owns_menu(cur, admin_id, menu_id):
                    return False, "내가 담당하는 매장의 메뉴가 아니어서 수정할 수 없습니다."
                cur.execute(
                    """UPDATE menu m JOIN store s ON m.store_id = s.store_id
                       SET m.price = %s, m.is_available = %s
                       WHERE m.menu_id = %s AND s.admin_id = %s""",
                    (price, bool(is_available), menu_id, admin_id),
                )
            conn.commit()
        return True, "저장되었습니다."
    except pymysql.MySQLError as e:
        return False, _friendly_error(e)


def add_menu(admin_id, store_id, menu_name, price, category_id, is_available=True):
    """새 메뉴 등록. 내 매장에만 등록할 수 있다. (직접 입력한 데이터라 is_sample = FALSE)"""
    menu_name = (menu_name or "").strip()
    if not menu_name:
        return False, "메뉴명을 입력해 주세요."
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                count = cur.execute(
                    """INSERT INTO menu (menu_name, price, is_available, store_id, category_id)
                       SELECT %s, %s, %s, s.store_id, %s
                       FROM store s WHERE s.store_id = %s AND s.admin_id = %s""",
                    (menu_name, price, bool(is_available), category_id, store_id, admin_id),
                )
            conn.commit()
        if count == 0:
            return False, "내가 담당하는 매장이 아니어서 등록할 수 없습니다."
        return True, f"'{menu_name}' 메뉴를 등록했습니다."
    except pymysql.MySQLError as e:
        return False, _friendly_error(e)


def delete_menu(admin_id, menu_id):
    """메뉴 삭제."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                count = cur.execute(
                    """DELETE m FROM menu m JOIN store s ON m.store_id = s.store_id
                       WHERE m.menu_id = %s AND s.admin_id = %s""",
                    (menu_id, admin_id),
                )
            conn.commit()
        if count == 0:
            return False, "내가 담당하는 매장의 메뉴가 아니어서 삭제할 수 없습니다."
        return True, "메뉴를 삭제했습니다."
    except pymysql.MySQLError as e:
        return False, _friendly_error(e)


# ---------------- 매장 등록·수정·삭제 ----------------

def _owns_store(cur, admin_id, store_id):
    cur.execute(
        "SELECT 1 FROM store WHERE store_id = %s AND admin_id = %s", (store_id, admin_id)
    )
    return cur.fetchone() is not None


def add_store(admin_id, store_name, store_type, location_info, building_id):
    """새 매장 등록. 담당 관리자는 로그인한 나 자신이 된다."""
    store_name = (store_name or "").strip()
    if not store_name:
        return False, "매장명을 입력해 주세요."
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO store (store_name, store_type, location_info, building_id, admin_id)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (store_name, store_type, (location_info or "").strip() or None,
                     building_id, admin_id),
                )
            conn.commit()
        return True, f"'{store_name}' 매장을 등록했습니다."
    except pymysql.MySQLError as e:
        return False, _friendly_error(e)


def update_store(admin_id, store_id, store_name, store_type, location_info, building_id):
    """매장 정보 수정."""
    store_name = (store_name or "").strip()
    if not store_name:
        return False, "매장명을 입력해 주세요."
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if not _owns_store(cur, admin_id, store_id):
                    return False, "내가 담당하는 매장이 아니어서 수정할 수 없습니다."
                cur.execute(
                    """UPDATE store
                       SET store_name = %s, store_type = %s, location_info = %s, building_id = %s
                       WHERE store_id = %s AND admin_id = %s""",
                    (store_name, store_type, (location_info or "").strip() or None,
                     building_id, store_id, admin_id),
                )
            conn.commit()
        return True, "저장되었습니다."
    except pymysql.MySQLError as e:
        return False, _friendly_error(e)


def delete_store(admin_id, store_id):
    """매장 삭제. 그 매장의 메뉴도 함께 삭제된다 (ON DELETE CASCADE)."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                count = cur.execute(
                    "DELETE FROM store WHERE store_id = %s AND admin_id = %s",
                    (store_id, admin_id),
                )
            conn.commit()
        if count == 0:
            return False, "내가 담당하는 매장이 아니어서 삭제할 수 없습니다."
        return True, "매장과 그 매장의 메뉴를 삭제했습니다."
    except pymysql.MySQLError as e:
        return False, _friendly_error(e)
