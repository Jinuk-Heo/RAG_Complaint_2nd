import psycopg2
import math
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np

# ==========================================
# 1. 설정 (DB 접속 정보)
# ==========================================
DB_CONFIG = { "host": "localhost", "database": "complaint_db", "user": "postgres", "password": "0000", "port": "5432" }
MODEL_NAME = 'mixedbread-ai/mxbai-embed-large-v1'

# ==========================================
# 2. 도구 상자 (거리/유사도 계산)
# ==========================================

def calculate_distance(lat1, lon1, lat2, lon2):
    """지점 간 거리 계산 (하버사인 공식) - 미터(m) 단위"""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 9999999 # 좌표 없으면 아주 먼 것으로 침
        
    R = 6371000
    try:
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    except:
        return 9999999

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# ==========================================
# 3. 핵심 로직 (군집화 실행)
# ==========================================

def run_clustering():
    print(f"[*] 모델 로딩 중... ({MODEL_NAME})")
    model = SentenceTransformer(MODEL_NAME)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 아직 사건 번호(incident_id)가 없는 민원들 가져오기
    # (주의: 벡터 데이터도 필요하므로 complaint_normalizations와 조인)
    print("[*] 처리할 민원 검색 중...")
    query = """
        SELECT 
            c.id, c.title, c.received_at, c.lat, c.lon, c.district_id,
            cn.embedding, c.body
        FROM complaints c
        JOIN complaint_normalizations cn ON c.id = cn.complaint_id
        WHERE c.incident_id IS NULL
        ORDER BY c.received_at ASC
    """
    cursor.execute(query)
    target_complaints = cursor.fetchall()
    
    print(f"[*] 총 {len(target_complaints)}개의 미분류 민원을 발견했습니다.")

    processed_count = 0
    new_incident_count = 0
    merged_count = 0

    for row in target_complaints:
        c_id, c_title, c_date, c_lat, c_lon, c_dist_id, c_embedding_str, c_body = row
        
        # 벡터 데이터 파싱 (문자열 -> 리스트)
        if isinstance(c_embedding_str, str):
            c_vector = json.loads(c_embedding_str)
        else:
            c_vector = c_embedding_str # 이미 리스트인 경우

        # ---------------------------------------------------------
        # [탐색] 내 구역(district_id)에서 '진행 중'인 사건들 후보 조회
        # ---------------------------------------------------------
        cursor.execute("""
            SELECT id, title, centroid_lat, centroid_lon, opened_at 
            FROM incidents 
            WHERE district_id = %s AND status != 'CLOSED'
        """, (c_dist_id,))
        
        candidates = cursor.fetchall()
        
        best_match_id = None
        best_score = 0
        
        # 후보 사건들을 하나씩 심사
        for cand in candidates:
            i_id, i_title, i_lat, i_lon, i_opened_at = cand
            
            # [검문 1] 거리 체크 (50m 이내)
            dist = calculate_distance(c_lat, c_lon, i_lat, i_lon)
            if dist > 50: continue # 탈락
            
            # [검문 2] 시간 체크 (7일 이내)
            # 날짜 형식이 다를 수 있어 안전하게 처리
            try:
                if isinstance(c_date, str): c_dt = datetime.strptime(c_date, "%Y-%m-%d %H:%M:%S")
                else: c_dt = c_date
                
                if isinstance(i_opened_at, str): i_dt = datetime.strptime(i_opened_at, "%Y-%m-%d %H:%M:%S")
                else: i_dt = i_opened_at
                
                time_diff = abs((c_dt - i_dt).days)
                if time_diff > 7: continue # 탈락
            except:
                continue # 날짜 계산 에러 시 건너뜀

            # [검문 3] 내용 유사도 체크 (AI)
            # 해당 사건의 대표 민원(가장 먼저 생긴 애)의 벡터를 가져와서 비교
            cursor.execute("""
                SELECT cn.embedding 
                FROM complaints c
                JOIN complaint_normalizations cn ON c.id = cn.complaint_id
                WHERE c.incident_id = %s
                ORDER BY c.received_at ASC
                LIMIT 1
            """, (i_id,))
            
            result = cursor.fetchone()
            if not result: continue
            
            i_embedding_data = result[0]
            if isinstance(i_embedding_data, str):
                i_vector = json.loads(i_embedding_data)
            else:
                i_vector = i_embedding_data
                
            # 코사인 유사도 계산
            score = cosine_similarity([c_vector], [i_vector])[0][0]
            
            # 0.9점 이상이면 합격! (가장 점수 높은 곳으로 감)
            if score >= 0.9 and score > best_score:
                best_score = score
                best_match_id = i_id
        
        # ---------------------------------------------------------
        # [결정] 병합 vs 신규 생성
        # ---------------------------------------------------------
        if best_match_id:
            # [병합] 기존 사건에 추가
            cursor.execute("""
                UPDATE complaints 
                SET incident_id = %s, incident_linked_at = NOW(), incident_link_score = %s, status = 'IN_PROGRESS'
                WHERE id = %s
            """, (best_match_id, float(best_score), c_id))
            merged_count += 1
            # print(f"   -> [병합] 민원 {c_id}번 -> 사건 {best_match_id}번 (유사도: {best_score:.2f})")
            
        else:
            # [신규] 새로운 사건 생성
            # incident 제목은 첫 민원의 제목을 따라감
            cursor.execute("""
                INSERT INTO incidents (title, district_id, centroid_lat, centroid_lon, opened_at, status)
                VALUES (%s, %s, %s, %s, %s, 'OPEN')
                RETURNING id
            """, (c_title, c_dist_id, c_lat, c_lon, c_date))
            
            new_incident_id = cursor.fetchone()[0]
            
            # 민원 업데이트 (내가 이 구역의 조장이다)
            cursor.execute("""
                UPDATE complaints 
                SET incident_id = %s, incident_linked_at = NOW(), incident_link_score = 1.0, status = 'IN_PROGRESS'
                WHERE id = %s
            """, (new_incident_id, c_id))
            new_incident_count += 1
            # print(f"   -> [신규] 민원 {c_id}번 -> 새 사건 {new_incident_id}번 생성")

        processed_count += 1
        if processed_count % 10 == 0:
            print(f"[*] 진행 중... ({processed_count}/{len(target_complaints)})")
            conn.commit() # 중간 저장

    conn.commit()
    conn.close()
    print("\n" + "="*50)
    print(f"[완료] 총 {processed_count}건 처리 완료")
    print(f" - 기존 사건 병합: {merged_count}건")
    print(f" - 신규 사건 생성: {new_incident_count}건")
    print("="*50)

if __name__ == "__main__":
    run_clustering()