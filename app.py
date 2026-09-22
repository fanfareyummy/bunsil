import streamlit as st
import random
from datetime import datetime

# -------------------------------------------------------------------
# Page Config & Custom CSS (모던하고 심플한 디자인 스타일 적용)
# -------------------------------------------------------------------
st.set_page_config(page_title="Find-It | 호치민시한국국제학교", page_icon="🔍", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 깔끔하게 정리 */
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 2.8em;
        background-color: #0066ff;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #0052cc; color: white; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 세션 상태 (가상 DB) 초기화
# -------------------------------------------------------------------
if "found_db" not in st.session_state:
    st.session_state.found_db = [
        {
            "id": 1,
            "title": "에어팟 프로 (하얀색)",
            "keywords": ["에어팟", "하얀색", "전자제품"],
            "location": "2층 과학실",
            "date": "2026-09-20",
            "status": "행정실 보관중",
            "detail_answer": "빨간색 스티커",
            "image": None
        },
        {
            "id": 2,
            "title": "파란색 체육복 상의",
            "keywords": ["체육복", "파란색", "의류"],
            "location": "체육관",
            "date": "2026-09-21",
            "status": "반환 예약됨",
            "detail_answer": "L사이즈",
            "image": None
        }
    ]

# AI 이미지 키워드 추출 가상 함수
def ai_analyze_image(file_name):
    name = file_name.lower()
    if "airpod" in name or "에어팟" in name:
        return ["에어팟", "전자제품", "하얀색"]
    elif "uniform" in name or "체육복" in name:
        return ["체육복", "의류", "파란색"]
    return ["소지품", "기타"]

# -------------------------------------------------------------------
# 사이드바 메뉴 (간결한 네비게이션)
# -------------------------------------------------------------------
with st.sidebar:
    st.title("🔍 Find-It")
    st.caption("호치민시한국국제학교 분실물 센터")
    st.divider()
    menu = st.radio("메뉴를 선택하세요", ["🔎 분실물 검색", "📸 습득물 등록", "📋 보관 현황 (관리자)"])
    st.divider()
    st.metric(label="현재 보관 중인 물품", value=f"{len(st.session_state.found_db)}개")

# -------------------------------------------------------------------
# 1. 분실물 검색 메인 화면 (심플 Card UI)
# -------------------------------------------------------------------
if menu == "🔎 분실물 검색":
    st.subheader("🔎 잃어버린 물건을 찾아보세요")
    
    # 검색창 및 필터
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("검색어 입력", placeholder="예: 에어팟, 체육복, 과학실", label_visibility="collapsed")
    with col_filter:
        location_filter = st.selectbox("장소 필터", ["전체", "2층 과학실", "체육관", "음악실", "운동장"], label_visibility="collapsed")

    # 검색 로직
    results = st.session_state.found_db
    if search_query:
        results = [i for i in results if any(search_query in k for k in i["keywords"]) or search_query in i["location"] or search_query in i["title"]]
    if location_filter != "전체":
        results = [i for i in results if i["location"] == location_filter]

    st.write(f"검색 결과: **{len(results)}**건")
    st.divider()

    # 물품 리스트 출력 (깔끔한 EXPANDER 카드 형태)
    for item in results:
        status_color = "🟢" if item["status"] == "행정실 보관중" else "🟡"
        with st.expander(f"{status_color} [{item['status']}] {item['title']} (습득 장소: {item['location']})"):
            st.write(f"📌 **등록일:** {item['date']}")
            st.write(f"🏷️ **태그:** {', '.join(['#' + k for k in item['keywords']])}")
            
            if item["status"] == "행정실 보관중":
                st.markdown("---")
                st.write("🔒 **본인 확인 퀴즈**")
                user_ans = st.text_input("물건의 세부 특징을 입력하세요 (예: 스티커 색상, 흠집 위치)", key=f"ans_{item['id']}")
                
                if st.button("내 물건 신청하기", key=f"btn_{item['id']}"):
                    if user_ans and user_ans.strip() in item["detail_answer"]:
                        item["status"] = "반환 예약됨"
                        pickup_code = f"PK-{random.randint(1000, 9999)}"
                        st.balloons()
                        st.success("✅ 본인 인증 완료!")
                        st.info(f"🔑 행정실 수령 코드: **{pickup_code}** (행정실에 제시하세요)")
                    else:
                        st.error("❌ 입력한 정보가 일치하지 않습니다. 다시 확인해 주세요.")
            else:
                st.warning("이미 반환 예약이 완료된 물품입니다.")

# -------------------------------------------------------------------
# 2. 습득물 등록 화면 (3단계 간단 입력)
# -------------------------------------------------------------------
elif menu == "📸 습득물 등록":
    st.subheader("📸 습득물 간편 등록")
    st.caption("주운 물건의 사진과 간단한 정보를 입력해 주세요.")

    with st.form("register_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("1. 물건 사진 업로드", type=["jpg", "png", "jpeg"])
        item_title = st.text_input("2. 물품명 (예: 파란색 에어팟 케이스)", placeholder="물건의 이름을 적어주세요")
        found_loc = st.selectbox("3. 습득 장소", ["2층 과학실", "체육관", "음악실", "중앙계단", "급식실", "운동장"])
        secret_feature = st.text_input("4. 본인 확인용 퀴즈 정답 (습득자만 아는 특징)", placeholder="예: 케이스 내부 빨간 스티커, L사이즈 표기 등")
        
        submitted = st.form_submit_button("🚀 등록 완료하기")
        
        if submitted:
            if uploaded_file and item_title and secret_feature:
                # AI 태그 추출
                extracted_tags = ai_analyze_image(uploaded_file.name)
                
                new_item = {
                    "id": len(st.session_state.found_db) + 1,
                    "title": item_title,
                    "keywords": extracted_tags,
                    "location": found_loc,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "status": "행정실 보관중",
                    "detail_answer": secret_feature,
                    "image": uploaded_file
                }
                st.session_state.found_db.append(new_item)
                st.success(f"🎉 성공적으로 등록되었습니다! (AI 자동 태그: {', '.join(extracted_tags)})")
            else:
                st.error("⚠️ 사진, 물품명, 퀴즈 정답을 모두 입력해 주세요.")

# -------------------------------------------------------------------
# 3. 관리자 보관 현황 (대시보드)
# -------------------------------------------------------------------
elif menu == "📋 보관 현황 (관리자)":
    st.subheader("📋 전체 보관 및 반환 현황")
    st.dataframe(
        st.session_state.found_db,
        column_config={
            "id": "번호",
            "title": "물품명",
            "keywords": "태그",
            "location": "습득 장소",
            "date": "등록일",
            "status": "상태",
            "detail_answer": "퀴즈 정답"
        },
        hide_index=True,
        use_container_width=True
    )
