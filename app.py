import streamlit as st
import random
import uuid

# -------------------------------------------------------------------
# Page Config & Custom Design (깔끔하고 세련된 스타일링)
# -------------------------------------------------------------------
st.set_page_config(page_title="Find-It | 학교 통합 분실물 시스템", page_icon="🔍", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9fbfd; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 2.8em;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #1d4ed8; color: white; }
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 0. 데이터베이스 및 함수 정의 (Pseudocode 반영)
# -------------------------------------------------------------------
if "database" not in st.session_state:
    st.session_state.database = []

def ai_image_analyze(item_image):
    """ai_image_analyze(item_image): 이미지명을 기반으로 키워드 자동 추출"""
    file_name = item_image.name.lower()
    if "airpod" in file_name or "에어팟" in file_name:
        return ["에어팟", "전자제품", "하얀색"]
    elif "uniform" in file_name or "체육복" in file_name:
        return ["체육복", "의류", "파란색"]
    return ["소지품", "기타"]

def generate_unique_id():
    """generate_unique_id(): 유니크 아이디 생성"""
    return str(uuid.uuid4())[:8]

def generate_pickup_code(item_id, user_id):
    """generate_pickup_code(item_id, user_id): 수령 픽업 코드 생성"""
    rand_num = random.randint(1000, 9999)
    return f"PK-{item_id.upper()}-{rand_num}"

# -------------------------------------------------------------------
# 사이드바 네비게이션
# -------------------------------------------------------------------
with st.sidebar:
    st.title("🔍 Find-It")
    st.caption("호치민시한국국제학교 분실물 센터")
    st.divider()
    menu = st.radio("메뉴를 선택하세요", ["📸 1. 습득물 등록", "🔎 2. 분실물 검색 및 신청", "🔑 3. 행정실 수령 관리"])
    st.divider()
    
    # 보관중인 물품 수 카운트
    active_items = len([i for i in st.session_state.database if i['status'] != '수령완료'])
    st.metric(label="현재 공개 등록된 물품", value=f"{active_items}개")

# -------------------------------------------------------------------
# 1. 습득물 등록 (Pseudocode: start ~ save_to_database)
# -------------------------------------------------------------------
if menu == "📸 1. 습득물 등록":
    st.subheader("📸 습득물 등록")
    st.caption("주운 물건의 정보를 입력하여 등록합니다.")

    with st.form("registration_form", clear_on_submit=True):
        item_image = st.file_uploader("input item_image", type=["jpg", "png", "jpeg"])
        found_location = st.selectbox("input found_location", ["2층 과학실", "체육관", "음악실", "중앙계단", "급식실", "운동장"])
        detail_feature = st.text_input("input detail_feature (본인 확인용 세부 특징)", placeholder="예: 케이스 내부 빨간 스티커, L사이즈 표기 등")
        
        submit_btn = st.form_submit_button("등록 완료")

        if submit_btn:
            if item_image and detail_feature:
                # Pseudocode 실행
                keywords = ai_image_analyze(item_image)
                item_id = generate_unique_id()
                
                new_item = {
                    "item_id": item_id,
                    "item_image": item_image.name,
                    "keywords": keywords,
                    "found_location": found_location,
                    "detail_feature": detail_feature,
                    "status": "행정실에서 보관중",
                    "pickup_code": None,
                    "claimed_by": None
                }
                
                # save_to_database
                st.session_state.database.append(new_item)
                st.success(f"✅ 등록 완료! [ID: {item_id}] (AI 추출 키워드: {', '.join(keywords)})")
            else:
                st.warning("⚠️ 이미지와 세부 특징을 모두 입력해 주세요.")

# -------------------------------------------------------------------
# 2. 분실물 검색 및 신청 (Pseudocode: while user_browsing do)
# -------------------------------------------------------------------
elif menu == "🔎 2. 분실물 검색 및 신청":
    st.subheader("🔎 분실물 검색 및 반환 신청")

    # input user_id, search_keyword
    col_user, col_search = st.columns([1, 2])
    with col_user:
        user_id = st.text_input("input user_id (학번/이름)", value="student1")
    with col_search:
        search_keyword = st.text_input("input search_keyword", placeholder="검색어를 입력하세요 (예: 에어팟, 체육관)")

    # db_search & display results
    # (Pseudocode: remove_from_public_list 조건에 따라 '수령완료' 건은 검색 목록에서 제외)
    public_list = [i for i in st.session_state.database if i["status"] != "수령완료"]

    if search_keyword:
        results = [
            item for item in public_list
            if search_keyword in item["found_location"] or any(search_keyword in k for k in item["keywords"])
        ]
    else:
        results = public_list

    st.write(f"검색 결과 **{len(results)}**건")
    st.divider()

    # display results & user_selects_item
    for item in results:
        status_color = "🟢" if item["status"] == "행정실에서 보관중" else "🟡"
        
        with st.expander(f"{status_color} [{item['status']}] 위치: {item['found_location']} | 태그: {', '.join(item['keywords'])}"):
            st.write(f"🆔 **물품 ID:** {item['item_id']}")
            st.write(f"📍 **습득 장소:** {item['found_location']}")
            st.write(f"🏷️ **키워드:** {', '.join(item['keywords'])}")
            st.write(f"📌 **현재 상태:** {item['status']}")

            # if user_selects_item(item_id)
            if item["status"] == "행정실에서 보관중":
                st.markdown("---")
                st.write("🔒 **본인 확인: 물건의 세부적 특징을 입력하세요.**")
                user_answer = st.text_input("input user_answer", key=f"ans_{item['item_id']}")

                if st.button("신청하기", key=f"btn_{item['item_id']}"):
                    # if user_answer contains detail_feature then
                    if user_answer and user_answer.strip() in item["detail_feature"]:
                        item["status"] = "반환 예약"
                        pickup_code = generate_pickup_code(item["item_id"], user_id)
                        item["pickup_code"] = pickup_code
                        item["claimed_by"] = user_id
                        
                        st.balloons()
                        st.success(f"인증을 완료했습니다! 행정실 수령용 코드: **{pickup_code}**")
                    else:
                        st.error("정보가 일치하지 않습니다. 타인의 물품은 신청할 수 없습니다.")
            elif item["status"] == "반환 예약":
                st.warning(f"이미 반환 예약된 물품입니다. (신청자: {item['claimed_by']})")

# -------------------------------------------------------------------
# 3. 행정실 관리자 수령 (Pseudocode: if admin_verifies_pickup_code)
# -------------------------------------------------------------------
elif menu == "🔑 3. 행정실 수령 관리":
    st.subheader("🔑 행정실 수령 관리 (관리자 전용)")
    st.caption("학생이 제시한 픽업코드를 검증하여 최종 반환 처리를 진행합니다.")

    input_code = st.text_input("학생의 픽업코드(pickup_code) 입력", placeholder="예: PK-AB1234-5678")

    if st.button("픽업코드 검증 및 반환 완료"):
        matched_item = None
        for item in st.session_state.database:
            if item["pickup_code"] == input_code.strip() and item["status"] == "반환 예약":
                matched_item = item
                break

        # if admin_verifies_pickup_code(pickup_code) then
        if matched_item:
            # update_status(item_id, '수령완료')
            matched_item["status"] = "수령완료"
            # remove_from_public_list(item_id) -> 다음 검색 시 제외됨
            st.success(f"✅ [ID: {matched_item['item_id']}] 물품의 반환 절차가 완료되었습니다!")
            st.info("해당 물품은 공개 검색 목록(public_list)에서 자동으로 제외되었습니다.")
        else:
            st.error("❌ 유효하지 않거나 이미 처리된 픽업코드입니다.")

    st.divider()
    st.write("📋 전체 DB 데이터 (테스트/확인용)")
    st.dataframe(st.session_state.database, use_container_width=True)
