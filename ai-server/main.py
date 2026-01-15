from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from app.services import llm_service
from app import database
from app.services.llm_service import LLMService
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import uuid
import os
import re
import json
import uuid
import requests
import textwrap
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai
from sqlalchemy import Integer, create_engine, Column, BigInteger, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

app = FastAPI(title="Complaint Analyzer AI")
llm_service = LLMService()

# (CORS 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 모든 곳에서 접속 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테스트
@app.get("/")
async def root():
    return {"message": "서버 연결 성공 "}

# Postman으로 보낼 데이터 구조 정의
class ComplaintRequest(BaseModel):
    title: str
    body: str
    district: str

@app.post("/analyze")
async def analyze_and_store(request: ComplaintRequest):
    try:
        print(f"[*] 분석 시작 - 민원 제목: {request.title}")

        # 1. LLM 요약 및 분석 (Normalization)
        # Ollama가 응답할 때까지 기다립니다.
        body = request.title + "\n" + request.body
        analysis = await llm_service.get_normalization(body)
        print(f"[*] 정규화 완료: {analysis}...")

        # 2. 벡터 추출 (Embedding)
        # 전처리된 민원 원본을 바탕으로 1024차원 벡터 생성
        embedding = await llm_service.get_embedding(analysis['preprocess_body'])
        analysis['embedding'] = embedding
        print(f"[*] 벡터화 완료 (차원: {len(embedding)})")

        # 3. DB 저장 (is_current 처리 포함 트랜잭션)
        # Python에서 PostgreSQL로 직접 저장
        complaint_id = database.save_complaint(request.title, request.body, request.district)
        database.save_normalization(complaint_id, analysis, embedding)
        print(f"[+] 성공: 민원 {complaint_id} 데이터베이스 저장 완료")

        return {
            "status": "success", 
            "complaint_id": complaint_id,
            **analysis,
        }

    except Exception as e:
        print(f"[!] 에러 발생: {str(e)}")
        # 클라이언트에게 500 에러와 원인 반환
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# 요청 데이터 구조 정의
class ChatRequest(BaseModel):
    query: str

# 민원 상세 화면 진입 시 (자동 분석 & 가이드)
@app.get("/api/complaints/{complaint_id}/ai-analysis")
async def get_ai_analysis(complaint_id: int):
    """
    [자동 모드]
    공무원이 민원을 클릭했을 때, DB에 있는 민원 내용을 바탕으로
    유사 사례 요약과 처리 방향 가이드를 자동으로 생성
    """
    try:
        # query 인자 없이 호출 -> llm_service 내부에서 '자동 모드'로 동작
        response = await llm_service.generate_rag_response(complaint_id)
        return {"status": "success", "result": response}
    except Exception as e:
        return {"status": "error", "message": f"AI 분석 실패: {str(e)}"}

# 챗봇에게 추가 질문하기 (Q&A)
@app.post("/api/complaints/{complaint_id}/chat")
async def chat_with_ai(complaint_id: int, request: ChatRequest):
    """
    [수동 모드]
    공무원이 채팅창에 질문(query)을 입력하면,
    해당 질문을 법률 용어로 변환 후 검색하여 답변
    """
    try:
        # query 인자 포함 호출 -> llm_service 내부에서 '수동 질문 모드'로 동작
        response = await llm_service.generate_rag_response(complaint_id, request.query)
        return {"status": "success", "result": response}
    except Exception as e:
        return {"status": "error", "message": f"답변 생성 실패: {str(e)}"}
    
@app.post("/api/complaints/analyze")
async def analyzeComplaints(title:str, body:str):
    api_key = 'sk-QoIqcyDiLSdNT-c7OBhfLV6WbkGNhVt1cdDuTzzrGyw'
    url = "http://localhost:7860/api/v1/run/69747d4a-850e-4e7e-b914-57ae3d008b96"  # The complete API endpoint URL for this flow

    # Request payload configuration
    payload = {
        "output_type": "chat",
        "input_type": "text",
        "input_value": "", # 기본값, 비워두기
        "tweaks": {
            "TextInput-제목": {"value": title},
            "TextInput-본문": {"value": body}
        }
    }
    payload["session_id"] = str(uuid.uuid4())

    headers = {"x-api-key": api_key}

    try:
        # Send API request
        response = requests.request("POST", url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes

        # Print response
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except ValueError as e:
        print(f"Error parsing response: {e}")
        


# DB 설정 (사용자, 비밀번호, 호스트, DB이름 수정 필요)
DATABASE_URL = "postgresql://postgres:sanghpw@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
try:
    with engine.connect() as conn:
        print("✅ DB 연결 성공! 주소:", DATABASE_URL)
except Exception as e:
    print("❌ DB 연결 실패! 주소를 확인하세요.")
    print("에러 내용:", e)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Gemini 설정
genai.configure(api_key="AIzaSyCfF0yXHFw-WDVy-VSdJaZaAaIaWpLuSeA")
model = genai.GenerativeModel('gemini-2.0-flash', generation_config={"response_mime_type": "application/json"})

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma2:2b"

# --- DB 테이블 모델 ---
class ComplaintNormalization(Base):
    __tablename__ = "complaint_normalizations"

    id = Column(BigInteger, primary_key=True, index=True)
    complaint_id = Column(BigInteger, nullable=False)
    district_id = Column(Integer, nullable=True)
    neutral_summary = Column(Text)
    core_request = Column(Text)
    core_cause = Column(Text)
    target_object = Column(String(120))
    keywords_jsonb = Column(JSONB)
    location_hint = Column(String(255))
    resp_dept = Column(String(100))
    routing_rank = Column(JSONB)
    created_at = Column(DateTime, default=datetime.now)

# 테이블 생성
Base.metadata.create_all(bind=engine)

# --- 요청 데이터 모델 ---
class ComplaintRequest(BaseModel):
    id: int # 민원 PK
    title: str
    content: str

def masking_by_ollama(text):
    if not text or text.strip() == "": return ""
    prompt = f"[Identity] 당신은 보안 필터입니다... [Input] {text}" # 기존 프롬프트 사용
    try:
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_URL, json=payload, timeout=40)
        return response.json().get('response', text).strip()
    except:
        return text # 실패 시 원본 혹은 Regex 결과 반환

@app.post("/api/complaints/preprocess")
async def preprocess_complaint(req: ComplaintRequest, request: Request):
    db = SessionLocal()
    body = await request.body()
    print(f"받은 원본 데이터: {body.decode()}")
    try:
        
        safe_title = masking_by_ollama(req.title)
        if safe_title is None: return None
        safe_content = masking_by_ollama(req.content)
        if safe_content is None: return None

        # 2. Gemini 구조화 분석 (테이블 컬럼에 맞춤)
        prompt = f"""
        당신은 대한민국 지자체 행정 데이터 분석 전문가입니다. 
        반드시 모든 필드를 **한국어(Korean)**로만 작성하십시오. 절대 영어를 사용하지 마십시오.
        
        [분석 지침]
        1. neutral_summary: 감정을 배제하고 상황을 객관적으로 한국어 1문장 요약.
        2. core_request: 민원인이 요구하는 사항을 한국어로 명확히 기술.
        3. core_cause: 문제의 원인을 한국어로 기술.
        4. target_object: 민원의 주된 대상물 (한국어 단축 명사).
        5. keywords: 검색용 핵심 한국어 단어 5개 배열.
        6. location_hint: 본문에 언급된 장소를 한국어로 추출.
        7. suggested_dept: 가장 적합한 한국어 부서 명칭.

        민원 제목: {safe_title}
        민원 내용: {safe_content}
        """

        response = model.generate_content(prompt)
        # JSON 문자열 추출 (Markdown 제거)
        clean_json = re.sub(r'```json|```', '', response.text).strip()
        analysis = json.loads(clean_json)
        
        if isinstance(analysis, list):
            if len(analysis) > 0:
                analysis = analysis[0]
            else:
                raise ValueError("Gemini returned an empty list")

        # 3. DB 저장 (complaint_normalizations)
        norm_entry = ComplaintNormalization(
            complaint_id=req.id,
            district_id=3,
            neutral_summary=analysis.get('neutral_summary'),
            core_request=analysis.get('core_request'),
            core_cause=analysis.get('core_cause'),
            target_object=analysis.get('target_object'),
            keywords_jsonb=analysis.get('keywords'),
            location_hint=analysis.get('location_hint'),
            resp_dept=analysis.get('suggested_dept'),
            routing_rank={"primary": analysis.get('suggested_dept'), "confidence": "high"}
        )

        try:
            db.add(norm_entry)
            db.commit()      # 여기서 에러가 나면 except로 빠집니다.
            db.refresh(norm_entry) # DB에서 생성된 ID를 다시 읽어옴

            print(f"--- DB 저장 완료! 생성된 ID: {norm_entry.id}, 참조 민원ID: {req.id}")
        except Exception as e:
            db.rollback()
            # 🚩 에러 내용을 아주 상세하게 출력하도록 수정
            import traceback
            print("!!! DB 저장 에러 발생 !!!")
            print(traceback.format_exc()) 
        
            # 에러 발생 시 성공 응답을 보내지 말고 에러 응답을 보냄
            raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 직접 실행을 위한 블록 (python main.py로 실행 가능)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

