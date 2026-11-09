"""일반 사용자 화면 (Streamlit)

실행: streamlit run app.py
기능 1 매장 조회 · 기능 2 검색/가격 정렬 · 기능 3 예산 추천 · 기능 4 카테고리 추천
"""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="교내 메뉴 통합 검색", layout="wide")

# ---------- DB 연결 확인 ----------
try:
    import db
except ModuleNotFoundError:
    st.error("`db_config.py` 파일이 없습니다. `db_config.example.py`를 복사해 `db_config.py`로 만들고 MySQL 비밀번호를 넣어 주세요.")
    st.stop()

try:
    categories = ["전체"] + [c["category_name"] for c in db.get_categories()]
except Exception as e:
    st.error(f"MySQL에 연결할 수 없습니다. MySQL 실행 여부와 `db_config.py`의 비밀번호를 확인해 주세요.\n\n오류: {e}")
    st.stop()


def sample_label(v):
    return "샘플" if v else ""


# ---------- 화면 ----------
st.title("교내 음식점·카페 메뉴 통합 검색")
st.caption("학생식당 · 음식점 · 카페의 메뉴와 가격을 한 번에 비교하세요.")

tab_menu, tab_store = st.tabs(["메뉴 추천 · 검색", "교내 매장 목록"])

# ===== 탭 1: 메뉴 추천·검색 (기능 2·3·4) =====
with tab_menu:
    with st.form("search_form"):
        keyword = st.text_input("메뉴명 또는 매장명 검색", placeholder="예: 덮밥, 카페")
        c1, c2, c3 = st.columns(3)
        with c1:
            budget = st.number_input(
                "최대 예산 (원)", min_value=0, max_value=50000, value=0, step=500,
                help="0이면 예산 제한 없이 검색합니다.",
            )
        with c2:
            category = st.selectbox("음식 종류", categories)
        with c3:
            order_label = st.radio("가격 정렬", ["낮은 순", "높은 순"], horizontal=True)
        st.form_submit_button("메뉴 추천받기", type="primary", width="stretch")

    rows = db.search_menus(
        keyword=keyword.strip(),
        max_price=budget or None,
        category=category,
        order="desc" if order_label == "높은 순" else "asc",
    )

    # 조건 요약
    conds = []
    if keyword.strip():
        conds.append(f"'{keyword.strip()}' 포함")
    if budget:
        conds.append(f"{budget:,}원 이하")
    if category != "전체":
        conds.append(category)
    summary = " · ".join(conds) if conds else "전체 메뉴"

    if not rows:
        st.warning(f"**{summary}** 조건에 맞는 메뉴가 없습니다. 예산을 늘리거나 음식 종류를 바꿔 보세요.")
    else:
        prices = [r["price"] for r in rows]
        m1, m2, m3 = st.columns(3)
        m1.metric("검색된 메뉴", f"{len(rows)}개")
        m2.metric("최저가", f"{min(prices):,}원")
        m3.metric("평균 가격", f"{round(sum(prices) / len(prices)):,}원")

        cheapest = min(rows, key=lambda r: r["price"])
        st.success(
            f"**{summary}** 조건에서 가장 저렴한 메뉴는 "
            f"**{cheapest['store_name']}의 {cheapest['menu_name']}** ({cheapest['price']:,}원)입니다."
        )

        df = pd.DataFrame(rows)
        df["위치"] = df["building_name"] + " " + df["location_info"].fillna("")
        df["비고"] = df["is_sample"].map(sample_label)
        df = df.rename(columns={
            "store_name": "매장명", "menu_name": "메뉴명", "price": "가격",
            "category_name": "종류", "store_type": "매장 유형",
        })[["매장명", "메뉴명", "가격", "종류", "매장 유형", "위치", "비고"]]

        st.dataframe(
            df, hide_index=True, width="stretch",
            column_config={"가격": st.column_config.NumberColumn("가격", format="%d원")},
        )

    if any(r["is_sample"] for r in rows):
        st.caption("※ '샘플' 표시는 개발용 가상 데이터입니다. 실제 교내 데이터로 교체될 예정입니다.")

# ===== 탭 2: 교내 매장 목록 (기능 1) =====
with tab_store:
    stores = db.get_stores()
    types = ["전체"] + sorted({s["store_type"] for s in stores})
    pick = st.radio("매장 유형", types, horizontal=True)
    if pick != "전체":
        stores = [s for s in stores if s["store_type"] == pick]

    if not stores:
        st.info("등록된 매장이 없습니다.")
    else:
        sdf = pd.DataFrame(stores)
        sdf["비고"] = sdf["is_sample"].map(sample_label)
        sdf = sdf.rename(columns={
            "store_name": "매장명", "store_type": "매장 유형", "building_name": "건물",
            "location_info": "상세 위치", "menu_count": "판매 중 메뉴 수",
        })[["매장명", "매장 유형", "건물", "상세 위치", "판매 중 메뉴 수", "비고"]]
        st.dataframe(sdf, hide_index=True, width="stretch")

        st.subheader("매장별 메뉴 보기")
        name = st.selectbox("매장 선택", [s["store_name"] for s in stores])
        menus = db.search_menus(keyword=name)
        menus = [m for m in menus if m["store_name"] == name]
        if menus:
            mdf = pd.DataFrame(menus).rename(columns={
                "menu_name": "메뉴명", "price": "가격", "category_name": "종류",
            })[["메뉴명", "가격", "종류"]]
            st.dataframe(
                mdf, hide_index=True, width="stretch",
                column_config={"가격": st.column_config.NumberColumn("가격", format="%d원")},
            )
        else:
            st.info("판매 중인 메뉴가 없습니다.")
