import math
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 모델 로딩
model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')

def calculate_distance(lat1, lon1, lat2, lon2):
    """지점 간 거리 계산 (보고서의 '지역 근접도' 기준)"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_similarity(text1, text2):
    """AI 유사도 산출 (보고서의 '유사도' 기준)"""
    vecs = model.encode([text1, text2])
    return cosine_similarity([vecs[0]], [vecs[1]])[0][0]

# ==========================================
# [허진욱 님 파트] 실제 군집화 판정 함수
# ==========================================
def judge_incident_link(new_complaint, existing_incident):
    """
    보고서 5, 8페이지 로직: 유사도, 지역, 시간 근접도를 모두 체크합니다.
    """
    # 1. 지역 근접도 체크 (50m 이내)
    dist = calculate_distance(new_complaint['lat'], new_complaint['lon'], 
                              existing_incident['lat'], existing_incident['lon'])
    if dist > 50: return False, 0
    
    # 2. 시간 근접도 체크 (보고서 준수: 최근 7일 이내 발생 건만 묶음)
    fmt = "%Y-%m-%d %H:%M:%S"
    d1 = datetime.strptime(new_complaint['date'], fmt)
    d2 = datetime.strptime(existing_incident['date'], fmt)
    days_diff = abs((d1 - d2).days)
    if days_diff > 7: return False, 0 # 7일 넘으면 별개 사건 

    # 3. 유사도 체크 (정밀도 향상을 위해 0.9로 상향)
    score = get_similarity(new_complaint['text'], existing_incident['text'])
    
    # 최종 판정: 0.9점 이상이면 같은 사건(incident_id)으로 연결 [cite: 21, 85]
    if score >= 0.9:
        return True, score
    else:
        return False, score

# --- 시뮬레이션 테스트 ---
incident_101 = {
    "text": "성북구청 앞 횡단보도 보도블럭 파손",
    "lat": 37.589400, "lon": 127.016900,
    "date": "2026-01-08 10:00:00"
}

# 아까 0.85가 나왔던 불법주차 민원
parking_complaint = {
    "text": "성북구청 정문 앞 불법주차 차량 신고합니다",
    "lat": 37.589400, "lon": 127.016900,
    "date": "2026-01-08 11:00:00"
}

is_linked, final_score = judge_incident_link(parking_complaint, incident_101)

if is_linked:
    print(f"🎉 사건 연결 성공! (유사도: {final_score:.2f})")
else:
    print(f"❌ 별개 사건으로 판명 (유사도: {final_score:.2f}) -> 새로운 사건(Incident) 생성 대상입니다.")