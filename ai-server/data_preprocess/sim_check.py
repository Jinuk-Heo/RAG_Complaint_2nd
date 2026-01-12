import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# DB 및 Ollama 설정
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "sanghpw",
    "port": 5432
}
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "mxbai-embed-large"

def get_embedding(text):
    """
    mxbai-embed-large 모델은 검색 시 'query: ' 접두사가 필수입니다.
    이게 없으면 DB에 저장된 'doc: ' 벡터와 거리 차이가 크게 발생합니다.
    """
    payload = {"model": EMBED_MODEL, "prompt": f"query: {text}"}
    try:
        res = requests.post(OLLAMA_URL, json=payload).json()
        return res.get('embedding')
    except Exception as e:
        print(f"Embedding Error: {e}")
        return None

def search_similar_complaints(input_text, top_k=5):
    # 1. 입력 민원 임베딩 생성 (mxbai 권장 query: 접두사 사용)
    query_vec = get_embedding(input_text)
    if not query_vec:
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 2. 하이브리드 검색 쿼리
        # (1 - (embedding <=> %s::vector)) : 벡터 유사도
        # ts_rank(search_vector, plainto_tsquery('simple', %s)) : 키워드 일치도
        
        search_sql = """
        SELECT 
            id, 
            resp_dept, 
            core_request, 
            (1 - (embedding <=> %s::vector)) AS v_score,
            ts_rank(search_vector, plainto_tsquery('simple', %s)) AS k_score
        FROM complaint_normalizations
        ORDER BY ( (1 - (embedding <=> %s::vector)) * 0.7 + 
                   ts_rank(search_vector, plainto_tsquery('simple', %s)) * 0.3 ) DESC
        LIMIT %s;
        """
        
        # %s가 총 5개입니다 (v_score용 1개, k_score용 1개, ORDER BY용 2개, LIMIT용 1개)
        # 하지만 중복 입력을 줄이기 위해 아래와 같이 인자를 구성합니다.
        cur.execute(search_sql, (
            query_vec,    # v_score 계산용
            input_text,   # k_score 계산용
            query_vec,    # ORDER BY 벡터 정렬용
            input_text,   # ORDER BY 키워드 정렬용
            top_k         # LIMIT용
        ))
        
        results = cur.fetchall()
        
        print(f"\n" + "="*60)
        print(f"🔍 하이브리드 검색 결과 (Vector 70% + Keyword 30%)")
        print("="*60)

        for i, row in enumerate(results, 1):
            # 두 점수를 합친 최종 신뢰도 계산
            final_score = (float(row['v_score']) * 0.7) + (float(row['k_score']) * 0.3)
            
            print(f"[{i}] 통합 점수: {final_score:.4f} (V: {row['v_score']:.3f}, K: {row['k_score']:.3f})")
            print(f"    - 담당 부서: {row['resp_dept']}")
            print(f"    - 핵심 요약: {row['core_request']}")
            print("-" * 60)

    except Exception as e:
        print(f"Search Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # 실제 테스트할 민원 (1차 모델이 요약한 형태라고 가정)
    new_complaint = "['작물 금지', '공공텃밭', '보복성 언행', '관리자 교육', '민원 처리']"
    
    search_similar_complaints(new_complaint)