"""엑셀(data/campus_menu.xlsx) → sql/seed_real.sql 변환기.

사용법
    python tools/excel_to_seed.py
    python tools/excel_to_seed.py --input 내파일.xlsx --output sql/seed_real.sql --admin-password 비밀번호

* 먼저 엑셀 내용을 검사한다. 오류가 하나라도 있으면 파일을 만들지 않고 오류 위치를 알려 준다.
* 만들어진 seed_real.sql 은 건물·관리자·카테고리·매장·메뉴를 모두 넣는다 (is_sample = FALSE).
  Workbench 에서 schema.sql → seed_real.sql 순서로 실행한다.
"""
import argparse
import sys
from pathlib import Path

import bcrypt
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
STORE_TYPES = ["학생식당", "일반음식점", "카페"]
CATEGORIES = ["한식", "중식", "일식", "양식", "분식", "음료", "디저트"]


def sql_str(value):
    """SQL 문자열 리터럴로 변환 (작은따옴표·역슬래시 이스케이프)."""
    s = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"


def cell_text(v):
    return "" if v is None else str(v).strip()


def read_rows(ws, ncols):
    """머리글을 뺀 행을 (엑셀 행 번호, [값...]) 로 돌려준다. 완전히 빈 행은 건너뛴다."""
    rows = []
    for r, row in enumerate(ws.iter_rows(min_row=2, max_col=ncols, values_only=True), start=2):
        values = [cell_text(v) if i != 2 or ws.title != "메뉴" else v for i, v in enumerate(row)]
        if all(cell_text(v) == "" for v in values):
            continue
        rows.append((r, values))
    return rows


def load(path):
    wb = load_workbook(path, data_only=True)
    for name in ("건물", "관리자", "매장", "메뉴"):
        if name not in wb.sheetnames:
            sys.exit(f"[오류] '{name}' 시트가 없습니다. tools/make_template.py 로 만든 양식을 써 주세요.")
    return (read_rows(wb["건물"], 1), read_rows(wb["관리자"], 2),
            read_rows(wb["매장"], 5), read_rows(wb["메뉴"], 5))


def validate(buildings, admins, stores, menus):
    errors = []

    def err(sheet, row, msg):
        errors.append(f"[{sheet} 시트 {row}행] {msg}")

    # 건물
    building_names = set()
    for r, (name,) in buildings:
        if not name:
            err("건물", r, "건물명이 비어 있습니다.")
        elif name in building_names:
            err("건물", r, f"건물 '{name}'이(가) 중복입니다.")
        building_names.add(name)

    # 관리자
    admin_ids = set()
    for r, (name, lid) in admins:
        if not name or not lid:
            err("관리자", r, "관리자명과 로그인아이디를 모두 적어 주세요.")
        elif lid in admin_ids:
            err("관리자", r, f"로그인아이디 '{lid}'이(가) 중복입니다.")
        admin_ids.add(lid)

    # 매장
    store_names = set()
    for r, (name, stype, bname, loc, aid) in stores:
        if not name:
            err("매장", r, "매장명이 비어 있습니다.")
        elif name in store_names:
            err("매장", r, f"매장 '{name}'이(가) 중복입니다.")
        store_names.add(name)
        if stype not in STORE_TYPES:
            err("매장", r, f"매장유형 '{stype}'은(는) 사용할 수 없습니다. {STORE_TYPES} 중에서 고르세요.")
        if bname not in building_names:
            err("매장", r, f"건물 '{bname}'이(가) 건물 시트에 없습니다.")
        if aid not in admin_ids:
            err("매장", r, f"담당관리자 '{aid}'이(가) 관리자 시트에 없습니다.")
        if bname and loc.startswith(bname):
            err("매장", r, f"상세위치 '{loc}'에 건물명이 들어 있습니다. 세부 위치만 적어 주세요.")

    # 메뉴
    seen = set()
    for r, (sname, mname, price, cat, avail) in menus:
        if sname not in store_names:
            err("메뉴", r, f"매장 '{sname}'이(가) 매장 시트에 없습니다.")
        if not mname:
            err("메뉴", r, "메뉴명이 비어 있습니다.")
        if cat not in CATEGORIES:
            err("메뉴", r, f"카테고리 '{cat}'은(는) 사용할 수 없습니다. {CATEGORIES} 중에서 고르세요.")
        if avail not in ("", "판매중", "판매중지"):
            err("메뉴", r, f"판매여부 '{avail}'은(는) '판매중' 또는 '판매중지'만 가능합니다.")
        try:
            p = int(price) if not isinstance(price, str) else int(price.replace(",", "").replace("원", "").strip())
            if p < 0 or (not isinstance(price, str) and float(price) != p):
                raise ValueError
        except (TypeError, ValueError):
            err("메뉴", r, f"가격 '{price}'은(는) 0 이상의 정수여야 합니다. (예: 5500)")
        if (sname, mname) in seen:
            err("메뉴", r, f"'{sname}'에 메뉴 '{mname}'이(가) 중복입니다.")
        seen.add((sname, mname))

    for need, label in ((buildings, "건물"), (admins, "관리자"), (stores, "매장"), (menus, "메뉴")):
        if not need:
            errors.append(f"[{label} 시트] 입력된 행이 없습니다.")
    return errors


def to_int_price(v):
    return int(v.replace(",", "").replace("원", "").strip()) if isinstance(v, str) else int(v)


def build_sql(buildings, admins, stores, menus, password):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    out = [
        "-- =========================================================",
        "-- 실제 교내 데이터 (is_sample = FALSE)",
        "-- tools/excel_to_seed.py 가 data/campus_menu.xlsx 에서 자동으로 만든 파일입니다.",
        "-- 직접 고치지 말고 엑셀을 고친 뒤 다시 변환하세요.",
        "-- 실행 순서: schema.sql → seed_real.sql",
        "-- =========================================================",
        "USE campus_food;",
        "",
        "INSERT INTO building (building_name) VALUES",
        ",\n".join(f"  ({sql_str(n)})" for _, (n,) in buildings) + ";",
        "",
        "INSERT INTO admin (admin_name, login_id, password_hash) VALUES",
        ",\n".join(f"  ({sql_str(n)}, {sql_str(lid)}, {sql_str(pw_hash)})" for _, (n, lid) in admins) + ";",
        "",
        "INSERT INTO category (category_name) VALUES",
        ",\n".join(f"  ({sql_str(c)})" for c in CATEGORIES) + ";",
        "",
        "INSERT INTO store (store_name, store_type, location_info, is_sample, building_id, admin_id) VALUES",
    ]
    rows = []
    for _, (name, stype, bname, loc, aid) in stores:
        rows.append(
            f"  ({sql_str(name)}, {sql_str(stype)}, {sql_str(loc) if loc else 'NULL'}, FALSE,\n"
            f"   (SELECT building_id FROM building WHERE building_name = {sql_str(bname)}),\n"
            f"   (SELECT admin_id FROM admin WHERE login_id = {sql_str(aid)}))")
    out.append(",\n".join(rows) + ";")
    out += ["", "INSERT INTO menu (menu_name, price, is_available, is_sample, store_id, category_id) VALUES"]
    rows = []
    for _, (sname, mname, price, cat, avail) in menus:
        rows.append(
            f"  ({sql_str(mname)}, {to_int_price(price)}, {'FALSE' if avail == '판매중지' else 'TRUE'}, FALSE,\n"
            f"   (SELECT store_id FROM store WHERE store_name = {sql_str(sname)}),\n"
            f"   (SELECT category_id FROM category WHERE category_name = {sql_str(cat)}))")
    out.append(",\n".join(rows) + ";")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="엑셀 → seed_real.sql 변환")
    ap.add_argument("--input", default=str(ROOT / "data" / "campus_menu.xlsx"))
    ap.add_argument("--output", default=str(ROOT / "sql" / "seed_real.sql"))
    ap.add_argument("--admin-password", default="admin1234",
                    help="관리자 계정 공통 비밀번호 (기본값은 테스트용 admin1234)")
    args = ap.parse_args()

    if not Path(args.input).exists():
        sys.exit(f"[오류] 엑셀 파일이 없습니다: {args.input}\n먼저 python tools/make_template.py 로 양식을 만드세요.")

    buildings, admins, stores, menus = load(args.input)
    errors = validate(buildings, admins, stores, menus)
    if errors:
        print(f"엑셀에서 오류 {len(errors)}개를 찾았습니다. 고친 뒤 다시 실행하세요.\n")
        print("\n".join(errors))
        sys.exit(1)

    Path(args.output).write_text(build_sql(buildings, admins, stores, menus, args.admin_password),
                                 encoding="utf-8", newline="\n")
    print(f"변환 완료 → {args.output}")
    print(f"  건물 {len(buildings)}개 · 관리자 {len(admins)}명 · 매장 {len(stores)}개 · 메뉴 {len(menus)}개")


if __name__ == "__main__":
    main()
