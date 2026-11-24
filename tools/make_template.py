"""데이터 수집용 엑셀 양식(data/campus_menu.xlsx)을 만든다.

실행: python tools/make_template.py
이미 data/campus_menu.xlsx 가 있으면 덮어쓰지 않는다 (입력한 데이터 보호).
양식을 새로 만들고 싶으면 기존 파일을 지우거나 이름을 바꾼 뒤 다시 실행한다.
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parent.parent / "data" / "campus_menu.xlsx"

STORE_TYPES = ["학생식당", "일반음식점", "카페"]
CATEGORIES = ["한식", "중식", "일식", "양식", "분식", "음료", "디저트"]
MAX_ROWS = 300  # 드롭다운을 적용할 행 수

HEADER_FILL = PatternFill("solid", fgColor="24364B")
HEADER_FONT = Font(bold=True, color="FFFFFF")
NOTE_FILL = PatternFill("solid", fgColor="FFF4CC")
THIN = Side(style="thin", color="D9D6CF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_header(ws, headers, widths):
    for col, (h, w) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(row=1, column=col, value=h)
        c.fill, c.font, c.border = HEADER_FILL, HEADER_FONT, BORDER
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[c.column_letter].width = w
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 24


def add_list_validation(ws, cell_range, formula, title, message):
    dv = DataValidation(type="list", formula1=formula, allow_blank=True,
                        showErrorMessage=True, errorTitle=title, error=message)
    ws.add_data_validation(dv)
    dv.add(cell_range)


def build():
    wb = Workbook()

    # ---------- 안내 ----------
    guide = wb.active
    guide.title = "안내"
    lines = [
        ("교내 음식점·카페 데이터 입력 양식", True),
        ("", False),
        ("입력 순서: ① 건물  ② 관리자  ③ 매장  ④ 메뉴  (앞 시트를 먼저 채워야 뒤 시트에서 드롭다운으로 고를 수 있습니다)", False),
        ("", False),
        ("규칙", True),
        ("1. 파란 머리글(첫 줄)은 건드리지 않습니다. 둘째 줄부터 입력합니다.", False),
        ("2. 매장유형 · 건물 · 담당관리자 · 매장명 · 카테고리는 드롭다운에서 고릅니다. 직접 쓰면 오타가 납니다.", False),
        ("3. 매장명은 매장 시트와 메뉴 시트에서 글자 하나까지 같아야 합니다. (드롭다운을 쓰면 자동으로 맞습니다)", False),
        ("4. 상세위치에는 건물명을 쓰지 않습니다. '1층', '지하 1층', '201호'처럼 세부 위치만 씁니다.", False),
        ("5. 가격은 숫자만 씁니다. 5500 (O) / 5,500원 (X)", False),
        ("6. 사이즈·HOT/ICE 가격이 다르면 메뉴를 나눠서 씁니다. 예: 아메리카노(R), 아메리카노(L)", False),
        ("7. 추가 옵션(곱빼기, 샷 추가 등)은 쓰지 않습니다. 기본 메뉴만 씁니다.", False),
        ("8. 판매여부는 비워 두면 '판매중'입니다. 지금 팔지 않는 메뉴만 '판매중지'로 고릅니다.", False),
        ("", False),
        ("다 채운 뒤: python tools/excel_to_seed.py  →  sql/seed_real.sql 이 만들어집니다.", False),
    ]
    for r, (text, bold) in enumerate(lines, start=1):
        c = guide.cell(row=r, column=1, value=text)
        c.font = Font(bold=bold, size=14 if r == 1 else 11)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    guide.column_dimensions["A"].width = 110

    # ---------- 목록 (드롭다운 원본) ----------
    lst = wb.create_sheet("목록")
    lst["A1"], lst["B1"] = "매장유형", "카테고리"
    for c in (lst["A1"], lst["B1"]):
        c.fill, c.font = HEADER_FILL, HEADER_FONT
    for i, v in enumerate(STORE_TYPES, start=2):
        lst.cell(row=i, column=1, value=v)
    for i, v in enumerate(CATEGORIES, start=2):
        lst.cell(row=i, column=2, value=v)
    lst["D1"] = "※ 드롭다운에 쓰는 값입니다. 수정하지 마세요."
    lst["D1"].fill = NOTE_FILL
    lst.column_dimensions["A"].width = 14
    lst.column_dimensions["B"].width = 14
    lst.column_dimensions["D"].width = 40

    # ---------- 건물 ----------
    b = wb.create_sheet("건물", 1)
    style_header(b, ["건물명"], [28])

    # ---------- 관리자 ----------
    a = wb.create_sheet("관리자", 2)
    style_header(a, ["관리자명", "로그인아이디"], [20, 20])
    for i, (name, lid) in enumerate(
            [("○○식당 관리자", "admin1")], start=2):
        a.cell(row=i, column=1, value=name)
        a.cell(row=i, column=2, value=lid)
    a["D1"] = "※ 비밀번호는 여기에 쓰지 않습니다. 변환할 때 한꺼번에 정합니다."
    a["D1"].fill = NOTE_FILL
    a.column_dimensions["D"].width = 52

    # ---------- 매장 ----------
    s = wb.create_sheet("매장", 3)
    style_header(s, ["매장명", "매장유형", "건물", "상세위치", "담당관리자(로그인아이디)"], [26, 14, 20, 22, 26])
    last = MAX_ROWS + 1
    add_list_validation(s, f"B2:B{last}", "=목록!$A$2:$A$20", "매장유형", "목록에서 고르세요.")
    add_list_validation(s, f"C2:C{last}", "=건물!$A$2:$A$50", "건물", "건물 시트에 먼저 입력하세요.")
    add_list_validation(s, f"E2:E{last}", "=관리자!$B$2:$B$50", "담당관리자", "관리자 시트에 있는 아이디만 가능합니다.")

    # ---------- 메뉴 ----------
    m = wb.create_sheet("메뉴", 4)
    style_header(m, ["매장명", "메뉴명", "가격(원)", "카테고리", "판매여부"], [26, 28, 12, 14, 12])
    add_list_validation(m, f"A2:A{MAX_ROWS * 5 + 1}", f"=매장!$A$2:$A${last}", "매장명", "매장 시트에 있는 매장만 가능합니다.")
    add_list_validation(m, f"D2:D{MAX_ROWS * 5 + 1}", "=목록!$B$2:$B$20", "카테고리", "목록에서 고르세요.")
    add_list_validation(m, f"E2:E{MAX_ROWS * 5 + 1}", '"판매중,판매중지"', "판매여부", "판매중 또는 판매중지")
    price_dv = DataValidation(type="whole", operator="greaterThanOrEqual", formula1="0",
                              allow_blank=True, showErrorMessage=True,
                              errorTitle="가격", error="0 이상의 숫자만 입력하세요. (예: 5500)")
    m.add_data_validation(price_dv)
    price_dv.add(f"C2:C{MAX_ROWS * 5 + 1}")

    return wb


if __name__ == "__main__":
    if OUT.exists():
        print(f"이미 있습니다: {OUT}\n입력한 데이터를 지키려고 덮어쓰지 않았습니다.")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        build().save(OUT)
        print(f"양식을 만들었습니다: {OUT}")
