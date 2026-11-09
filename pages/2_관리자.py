"""관리자 화면 (Streamlit) - 팀원 A 담당

로그인한 관리자는 자기가 담당하는 매장의 메뉴·매장 정보만 등록·수정·삭제할 수 있다.
변경 내용은 곧바로 MySQL 에 저장되고, 사용자 화면(app.py)에서 다시 검색하면 반영된다.
"""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="관리자 - 교내 메뉴", layout="wide")

try:
    import admin_db
    import db
except ModuleNotFoundError:
    st.error("`db_config.py` 파일이 없습니다. `db_config.example.py`를 복사해 `db_config.py`로 만들고 MySQL 비밀번호를 넣어 주세요.")
    st.stop()


def flash(kind, message):
    """다음 화면 맨 위에 보여줄 안내 문구를 저장한다."""
    st.session_state["flash"] = (kind, message)


def show_flash():
    if "flash" in st.session_state:
        kind, message = st.session_state.pop("flash")
        (st.success if kind == "success" else st.error)(message)


def done(result):
    """(성공 여부, 문구)를 받아 안내를 저장하고 화면을 새로 그린다."""
    ok, message = result
    flash("success" if ok else "error", message)
    st.rerun()


# ================= 로그인 =================
if "admin" not in st.session_state:
    st.title("관리자 로그인")
    st.caption("매장 담당자 계정으로 로그인하면 담당 매장의 메뉴와 정보를 관리할 수 있습니다.")
    show_flash()

    with st.form("login_form"):
        login_id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인", type="primary")

    if submitted:
        try:
            admin = admin_db.login(login_id.strip(), password)
        except Exception as e:
            st.error(f"MySQL에 연결할 수 없습니다. 오류: {e}")
            st.stop()
        if admin:
            st.session_state["admin"] = admin
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    st.stop()

# ================= 로그인 후 =================
admin = st.session_state["admin"]
admin_id = admin["admin_id"]

top_left, top_right = st.columns([5, 1])
top_left.title("관리자 화면")
top_left.caption(f"{admin['admin_name']}님, 로그인되었습니다. 담당 매장의 정보만 관리할 수 있습니다.")
if top_right.button("로그아웃"):
    del st.session_state["admin"]
    flash("success", "로그아웃되었습니다.")
    st.rerun()

show_flash()

stores = admin_db.get_my_stores(admin_id)
categories = db.get_categories()
buildings = admin_db.get_buildings()
cat_name = {c["category_id"]: c["category_name"] for c in categories}
bld_name = {b["building_id"]: b["building_name"] for b in buildings}


def yn(v):
    return "판매 중" if v else "품절"


def sample_label(v):
    return "샘플" if v else ""


tab_menu, tab_store = st.tabs(["메뉴 관리", "매장 관리"])

# ================= 탭 1: 메뉴 관리 =================
with tab_menu:
    if not stores:
        st.info("담당 매장이 없습니다. '매장 관리' 탭에서 매장을 먼저 등록해 주세요.")
    else:
        store_ids = [s["store_id"] for s in stores]
        store_label = {s["store_id"]: s["store_name"] for s in stores}

        pick_store = st.selectbox(
            "매장 선택", ["전체"] + store_ids,
            format_func=lambda x: "내 모든 매장" if x == "전체" else store_label[x],
        )
        menus = admin_db.get_my_menus(admin_id, None if pick_store == "전체" else pick_store)

        st.subheader(f"메뉴 {len(menus)}개")
        if menus:
            df = pd.DataFrame(menus)
            df["판매 여부"] = df["is_available"].map(yn)
            df["비고"] = df["is_sample"].map(sample_label)
            df = df.rename(columns={
                "store_name": "매장명", "menu_name": "메뉴명", "price": "가격",
                "category_name": "종류", "updated_at": "마지막 수정",
            })[["매장명", "메뉴명", "가격", "종류", "판매 여부", "마지막 수정", "비고"]]
            st.dataframe(
                df, hide_index=True, width="stretch",
                column_config={"가격": st.column_config.NumberColumn("가격", format="%d원")},
            )
        else:
            st.info("등록된 메뉴가 없습니다. 아래에서 새 메뉴를 등록해 보세요.")

        # ---- 수정 ----
        if menus:
            st.subheader("메뉴 수정 (가격 · 판매 여부)")
            by_id = {m["menu_id"]: m for m in menus}
            mid = st.selectbox(
                "수정할 메뉴", list(by_id),
                format_func=lambda i: f"{by_id[i]['store_name']} · {by_id[i]['menu_name']} "
                                      f"({by_id[i]['price']:,}원)",
            )
            m = by_id[mid]
            with st.form(f"edit_menu_{mid}"):
                new_price = st.number_input(
                    "가격 (원)", min_value=0, max_value=100000, step=100, value=int(m["price"]))
                new_avail = st.checkbox("판매 중", value=bool(m["is_available"]))
                if st.form_submit_button("저장", type="primary"):
                    done(admin_db.update_menu(admin_id, mid, int(new_price), new_avail))

            with st.expander("이 메뉴 삭제"):
                st.warning(f"'{m['menu_name']}' 메뉴가 삭제됩니다. 되돌릴 수 없습니다.")
                sure = st.checkbox("삭제하겠습니다", key=f"sure_menu_{mid}")
                if st.button("메뉴 삭제", disabled=not sure, key=f"del_menu_{mid}"):
                    done(admin_db.delete_menu(admin_id, mid))

        # ---- 등록 ----
        st.subheader("새 메뉴 등록")
        with st.form("add_menu", clear_on_submit=True):
            a1, a2 = st.columns(2)
            new_store = a1.selectbox("매장", store_ids, format_func=lambda i: store_label[i])
            new_cat = a2.selectbox("음식 종류", list(cat_name), format_func=lambda i: cat_name[i])
            new_name = st.text_input("메뉴명")
            b1, b2 = st.columns(2)
            price0 = b1.number_input("가격 (원)", min_value=0, max_value=100000, step=100, value=5000)
            avail0 = b2.checkbox("판매 중", value=True)
            if st.form_submit_button("등록"):
                done(admin_db.add_menu(admin_id, new_store, new_name, int(price0), new_cat, avail0))

# ================= 탭 2: 매장 관리 =================
with tab_store:
    st.subheader(f"내 매장 {len(stores)}개")
    if stores:
        sdf = pd.DataFrame(stores)
        sdf["비고"] = sdf["is_sample"].map(sample_label)
        sdf = sdf.rename(columns={
            "store_name": "매장명", "store_type": "매장 유형", "building_name": "건물",
            "location_info": "상세 위치", "menu_count": "메뉴 수",
        })[["매장명", "매장 유형", "건물", "상세 위치", "메뉴 수", "비고"]]
        st.dataframe(sdf, hide_index=True, width="stretch")

        st.subheader("매장 정보 수정")
        by_sid = {s["store_id"]: s for s in stores}
        sid = st.selectbox("수정할 매장", list(by_sid), format_func=lambda i: by_sid[i]["store_name"])
        s = by_sid[sid]
        with st.form(f"edit_store_{sid}"):
            e_name = st.text_input("매장명", value=s["store_name"])
            e1, e2 = st.columns(2)
            e_type = e1.selectbox("매장 유형", admin_db.STORE_TYPES,
                                  index=admin_db.STORE_TYPES.index(s["store_type"]))
            b_ids = list(bld_name)
            e_bld = e2.selectbox("건물", b_ids, format_func=lambda i: bld_name[i],
                                 index=b_ids.index(s["building_id"]))
            e_loc = st.text_input("상세 위치 (건물명 없이, 예: 1층, 지하 1층)",
                                  value=s["location_info"] or "")
            if st.form_submit_button("저장", type="primary"):
                done(admin_db.update_store(admin_id, sid, e_name, e_type, e_loc, e_bld))

        with st.expander("이 매장 삭제"):
            st.warning(f"'{s['store_name']}' 매장과 그 매장의 메뉴 {s['menu_count']}개가 "
                       f"모두 삭제됩니다. 되돌릴 수 없습니다.")
            sure_s = st.checkbox("삭제하겠습니다", key=f"sure_store_{sid}")
            if st.button("매장 삭제", disabled=not sure_s, key=f"del_store_{sid}"):
                done(admin_db.delete_store(admin_id, sid))

    st.subheader("새 매장 등록")
    with st.form("add_store", clear_on_submit=True):
        n_name = st.text_input("매장명")
        n1, n2 = st.columns(2)
        n_type = n1.selectbox("매장 유형", admin_db.STORE_TYPES)
        nb_ids = list(bld_name)
        n_bld = n2.selectbox("건물", nb_ids, format_func=lambda i: bld_name[i])
        n_loc = st.text_input("상세 위치 (건물명 없이, 예: 1층, 지하 1층)")
        st.caption("새 매장의 담당 관리자는 지금 로그인한 나로 등록됩니다.")
        if st.form_submit_button("등록"):
            done(admin_db.add_store(admin_id, n_name, n_type, n_loc, n_bld))
