import pandas as pd
import google.generativeai as genai
import json
import os
import time
import re
from tqdm import tqdm
import requests
import textwrap

# ================= 설정 섹션 =================
# Ollama 설정 (보안 필터)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma2:2b"

# Gemini 설정 (행정 분석)
API_KEY = "AIzaSyCfF0yXHFw-WDVy-VSdJaZaAaIaWpLuSeA"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash', generation_config={"response_mime_type": "application/json"})

INPUT_PATH = "./강동구.csv"
OUTPUT_PATH = "./강동구_structured_final.csv"
SAVE_INTERVAL = 10
FILTER_DATE = "2020-01-01" 
DISPLAY_WIDTH = 80 # 터미널 가로 너비 설정
# =============================================

def print_log(label, text, color_code="0"):
    """가독성을 위해 줄바꿈 및 길이 제한을 적용한 출력 함수"""
    # 너무 길면 200자까지만 표시 (확인용)
    wrapped_text = textwrap.fill(text, width=DISPLAY_WIDTH)
    print(f"\033[{color_code}m[{label}]\033[0m\n{wrapped_text}\n")

def masking_by_ollama(text):
    """Ollama를 사용하여 문맥 기반 개인정보 마스킹 (1차 보안 필터)"""
    if not text or not isinstance(text, str) or text.strip() == "": return ""
    
    prompt = f"""
    [Identity]
    당신은 텍스트의 형식을 100% 유지하며 개인정보만 가리는 '보안 필터'입니다.

    [Strict Rules]
    1. 반드시 한글로만 출력하십시오. 절대 영문으로 번역하지 마십시오.
    2. 입력된 문장의 구조, 숫자, 단어를 절대 수정하거나 요약하지 마십시오.
    3. 이름, 전화번호, 이메일, 상세 주소(동/호수)만 '[PII_MASKED]'로 교체하십시오.
    4. 다음 항목은 개인정보가 아니므로 절대 마스킹하지 말고 그대로 유지하십시오:
       - 문장 맨 앞의 번호 (예: 1., 2., 3., 가., 나.)
       - 행정 구역 지명 (예: 상일동, 강일동, 고덕동)
       - 아파트 단지 명칭 (예: 고덕3단지, 리엔파크 등)
       - 금액 및 날짜 (예: 1,000억원, 2024년 1월 1일)
    5. 부연 설명 없이 오직 마스킹된 결과 본문만 출력하십시오.

    [Example]
    입력: 1.상일동 고덕3단지 홍길동(010-1111-2222)은 101동 102호에 거주합니다.
    출력: 1.상일동 고덕3단지 [PII_MASKED]([PII_MASKED])은 [PII_MASKED]에 거주합니다.

    [Input Text]
    {text}

    [Output]
    """
    try:
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_URL, json=payload, timeout=40)
        return response.json().get('response', text).strip()
    except Exception as e:
        # 오류 발생 시 None 반환 (실패 신호)
        print(f"\n[Ollama Masking Error]: {e}")
        return None

def mask_complaint_regex(text, requester_name=None):
    """패턴 기반 마스킹 (민원용: 지명 숫자 보존)"""
    if not isinstance(text, str) or text.strip() == "": return ""
    if requester_name and len(str(requester_name)) >= 2:
        text = text.replace(str(requester_name), "[NAME_MASKED]")
    text = re.sub(r'\d{2,3}-\d{3,4}-\d{4}', '[PHONE_MASKED]', text)
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_MASKED]', text)
    return text

def mask_response_regex(text):
    """패턴 기반 마스킹 (답변용: 공무원 정보 제거)"""
    if not isinstance(text, str) or text.strip() == "": return ""
    staff_pattern = r'(\w+(?:과|소|동|부|팀|센터|공사|구청|주민센터|보건소))\s?\((?:담당\s?)?[가-힣0-9*○Xx]{2,4}.*?(?:\d{2,3}-\d{3,4}-\d{4}|\[PHONE_MASKED\])\)'
    text = re.sub(staff_pattern, r'\1([STAFF_INFO_MASKED])', text)
    text = re.sub(r'[가-힣][0-9*○Xx]{1,2}', '[NAME_MASKED]', text)
    text = re.sub(r'\d{2,3}-\d{3,4}-\d{4}', '[PHONE_MASKED]', text)
    return text

def get_structured_data(row):
    """Ollama 보안 필터 적용 후 Gemini 구조화 수행"""
    user_name = row.get('req_p', None)

    # --- 모니터링을 위한 출력 ---
    print("\n" + "="*DISPLAY_WIDTH)
    print(f" 현재 처리 중: {row['req_title']}")
    print("-" * DISPLAY_WIDTH)
    
    # 1단계: 원본 출력
    print_log("원본 내용", row['req_content'], "34") # 파란색
    
    # [1단계] 로컬 Regex 마스킹 (빠름)
    m_title = mask_complaint_regex(row['req_title'], requester_name=user_name)
    m_content = mask_complaint_regex(row['req_content'], requester_name=user_name)
    m_resp = mask_response_regex(row['resp_content'])

    # [2단계] 로컬 Ollama 보안 필터
    # 각 단계에서 None이 반환되면 즉시 리턴하여 해당 행 스킵
    safe_title = masking_by_ollama(m_title)
    if safe_title is None: return None
    safe_content = masking_by_ollama(m_content)
    if safe_content is None: return None
    safe_resp = masking_by_ollama(m_resp)
    if safe_resp is None: return None

    print_log("마스킹 결과", safe_content, "32") # 초록색
    print("="*DISPLAY_WIDTH)

    # [3단계] Gemini 분석 (제목/내용 통합 분석 버전)
    prompt = f"""
    당신은 지자체 행정 데이터 분석 및 RAG 시스템 전문가입니다. 
    제공된 '제목'과 '내용'을 대등하게 검토하여, 민원인의 진짜 의도를 파악하십시오.

    [분석 원칙]
    - 본문(내용)이 짧거나 "제목 참조"와 같은 식일 경우, 제목에 포함된 키워드를 바탕으로 모든 필드를 작성하십시오.
    - 로컬 보안 필터를 거친 안전한 데이터([PII_MASKED] 등)를 사용하십시오.

    [분석 지침]
    1. topic: 제목과 내용을 종합하여 민원의 핵심 요구사항을 '현상' 중심으로 1문장 요약하십시오.
    2. legal: 답변에서 언급된 구체적인 법령/조례 명칭을 추출하십시오. 없으면 "해당 없음" 표기.
    3. keywords: 검색용 핵심 행정 명사 5개를 추출하십시오. 제목의 핵심 키워드를 반드시 포함하십시오.
    4. category: 민원을 처리할 적절한 '행정 도메인'을 분류하십시오. (예: 도로교통, 환경위생, 세무, 사회복지, 주택건축, 푸른도시, 공원녹지 등)

    [민원 정보]
    - 제목: {safe_title}
    - 내용: {safe_content}
    - 답변(참고): {safe_resp}

    [JSON 응답 형식]
    {{
        "topic": "요약 문장",
        "legal": "법적 근거",
        "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
        "category": "행정 분류"
    }}
    """
    try:
        response = model.generate_content(prompt)
        p = json.loads(response.text)
        if isinstance(p, list): p = p[0]
        p['search_text'] = f"{p.get('topic')} {', '.join(p.get('keywords', []))} {p.get('category')}"
        return p
    except Exception as e:
        print(f"\n[Gemini API Error]: {e}")
        return None

# --- 메인 로직 시작 ---

if os.path.exists(OUTPUT_PATH):
    print(f"기존 작업 파일('{OUTPUT_PATH}')을 로드하여 재개합니다.")
    df = pd.read_csv(OUTPUT_PATH)
else:
    print(f"새로운 분석 작업을 시작합니다. (2020년 이후 필터링 적용)")
    df_raw = pd.read_csv(INPUT_PATH)
    df_raw['req_date_dt'] = pd.to_datetime(df_raw['req_date'], format='mixed', errors='coerce')
    df_raw = df_raw.dropna(subset=['req_date_dt'])
    df = df_raw[df_raw['req_date_dt'] >= FILTER_DATE].copy()
    
    for col in ['topic', 'legal_basis', 'keywords', 'category', 'search_text']:
        df[col] = None

target_indices = df[df['topic'].isna()].index
print(f"처리 대기 건수: {len(target_indices)}건 (건당 약 10~15초 예상)")

try:
    for idx in tqdm(target_indices, desc="보안 필터링 및 분석 중"):
        result = get_structured_data(df.loc[idx])
        if result:
            df.at[idx, 'topic'] = result.get('topic')
            df.at[idx, 'legal_basis'] = result.get('legal')
            df.at[idx, 'keywords'] = str(result.get('keywords'))
            df.at[idx, 'category'] = result.get('category')
            df.at[idx, 'search_text'] = result.get('search_text')
            
            if (target_indices.get_loc(idx) + 1) % SAVE_INTERVAL == 0:
                df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
        
        # Gemini RPM 제한(15회/분) + Ollama 부하 고려
        time.sleep(4) 

except KeyboardInterrupt:
    print("\n사용자에 의해 중단되었습니다. 저장 중...")
finally:
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"완료! 최종 결과 파일: {OUTPUT_PATH}")