pip install streamlit
import streamlit as st
import random
from datetime import datetime

# -------------------------------------------------------------------
# 0. 세션 상태(가상 데이터베이스) 초기화
# -------------------------------------------------------------------
if "found_db" not in st.session_state:
    st.session_state.found_db = [
        {
            "id": 1,
            "keywords": ["에어팟", "하얀색", "전자제품"],
            "location": "체육관",
            "date": "2026-09-20",
            "status": "보관중",
            "detail_answer": "철가루 방지 스티커가 빨간색임",
            "image_name": "airpods_sample.png"
        }
    ]

if "lost_reports" not in st.session_state:
    st.session_state.lost_reports = [
        {"user_id": "student111", "keywords": ["에어팟", "전자제품"], "location": "체육관"}
    ]

if "notifications" not in st.session_state:
    st.session_state.notifications = []


# -------------------------------------------------------------------
# AI 이미지 분석 모듈 (가상 함수)
# -------------------------------------------------------------------
def ai_image_analysis(image_file):
    """
    실제 AI Vision API(예: OpenAI Vision / YOLO / Google Vision)를 연동하는 파트입니다.
    프로토타입 구현을 위해 이미지 이름을 기반으로 자동 태깅을 흉내냅니다.
    """
    file_name = image_file.name.lower()
    tags = []
    
    if "airpod" in file_name or "에어팟" in file_name:
        tags = ["에어팟", "하얀색", "전자제품"]
    elif "uniform" in file_name or "체육복" in file_name:
        tags = ["체육복", "파란색", "의류"]
    else:
        tags = ["소지품", "잡화", "기타"]
        
    return tags


# -------------------------------------------------------------------
# Streamlit UI 레이아웃
# -------------------------------------------------------------------
st.set_page_config(page_title="Find-It | 학교 통합 분실물 시스템", layout="wide")
st.title("🔍 Find-It : 학교 통합 분실물 관리 시스템")

# 탭 구성 (의사코드의 1, 2, 3 단계)
tab1, tab2, tab3 = st.tabs(["1. 습득물 등록 (AI 분석)", "2. 분실물 검색 및 반환 신청", "3. 알림 및 보관함 상태"])


# ===================================================================
# 1. 습득자: 분실물 등록 & 매칭 검사
# ===================================================================
with tab1:
    st.subheader("📸 습득물 사진 등록")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("습득한 물건의 사진을 업로드하세요", type=["jpg", "png", "jpeg"])
        found_location = st.selectbox("습득 장소", ["체육관", "음악실", "중앙계단", "급식실", "운동장", "기타"])
        detail_answer = st.text_input("본인 확인용 세부 특징 입력 (예: 케이스 내부 스티커 색상, 흠집 위치 등)")
        
    with col2:
        if uploaded_file is not None:
            st.image(uploaded_file, caption="업로드된 습득물 이미지", width=300)
            
            if st.button("AI 태깅 및 등록 실행"):
                # 1. AI 연동 사진 분석 및 카테고리 추출
                extracted_keywords = ai_image_analysis(uploaded_file)
                st.success(f"🤖 AI가 추출한 키워드 태그: {extracted_keywords}")
                
                # DB 저장
                new_id = len(st.session_state.found_db) + 1
                new_item = {
                    "id": new_id,
                    "keywords": extracted_keywords,
                    "location": found_location,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "status": "보관중",
                    "detail_answer": detail_answer,
                    "image_name": uploaded_file.name
                }
                st.session_state.found_db.append(new_item)
                
                # 2. 분실물 데이터베이스 매칭 검사
                for report in st.session_state.lost_reports:
                    # 키워드 매칭 여부 확인
                    common_keywords = set(report["keywords"]).intersection(set(extracted_keywords))
                    if common_keywords and report["location"] == found_location:
                        notif_msg = f"🔔 [{report['user_id']}] 님! 등록하신 분실물과 유사한 물건이 {found_location}에서 습득되었습니다."
                        st.session_state.notifications.append(notif_msg)
                        st.info(f"매칭 알림 발송 완료: {notif_msg}")


# ===================================================================
# 3. 분실자: 물건 찾기 및 반환 신청
# ===================================================================
with tab2:
    st.subheader("🔎 습득물 검색 및 '내 물건' 신청")
    
    search_keyword = st.text_input("검색어를 입력하세요 (예: 에어팟, 체육복)")
    
    # DB 검색
    if search_keyword:
        results = [
            item for item in st.session_state.found_db 
            if any(search_keyword in k for k in item["keywords"]) or search_keyword in item["location"]
        ]
    else:
        results = st.session_state.found_db

    st.write(f"검색 결과 총 **{len(results)}**건")
    
    for item in results:
        with st.expander(f"[{item['status']}] {item['keywords']} | 습득 장소: {item['location']} ({item['date']})"):
            st.write(f"태그: {item['keywords']}")
            st.write(f"현재 상태: **{item['status']}**")
            
            if item["status"] == "보관중":
                user_answer = st.text_input(f"본인 확인 질문: 물건의 상세 특징을 입력하세요.", key=f"ans_{item['id']}")
                
                if st.button("반환 신청하기", key=f"btn_{item['id']}"):
                    # 입력값 비교 (유사도 체크)
                    if user_answer and user_answer.strip() in item["detail_answer"]:
                        item["status"] = "반환예약"
                        pickup_code = f"PK-{random.randint(1000, 9999)}"
                        st.balloons()
                        st.success(f"✅ 본인 인증 성공! 상태가 [반환예약]으로 변경되었습니다.")
                        st.warning(f"🔑 행정실 방문 픽업 코드: **{pickup_code}** (행정실 교사에게 제시하세요)")
                    else:
                        st.error("❌ 입력한 특징 정보가 일치하지 않습니다. 다시 확인해주세요.")


# ===================================================================
# 알림 및 보관함 현황
# ===================================================================
with tab3:
    st.subheader("🔔 실시간 자동 알림 목록")
    if st.session_state.notifications:
        for notif in st.session_state.notifications:
            st.info(notif)
    else:
        st.write("새로운 알림이 없습니다.")
        
    st.divider()
    st.subheader("📋 전체 습득물 데이터베이스 현황")
    st.dataframe(st.session_state.found_db)
