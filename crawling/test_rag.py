import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings # 만약 OpenAI 임베딩을 썼다면 이거
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 1. 환경변수 로드 (API 키 등)
load_dotenv()

# ==========================================
# [중요] 여기는 test_search.py와 설정이 같아야 합니다!
# ==========================================
# 저장된 DB 경로 (test_search.py에 있는 경로 확인)
PERSIST_DIRECTORY = "./db"  
# 임베딩 모델 (데이터 저장할 때 쓴 것과 같은 것이어야 함)
embedding_model = OpenAIEmbeddings() 
# ==========================================

def run_rag():
    print("📂 1. 벡터 DB를 연결하는 중...")
    if not os.path.exists(PERSIST_DIRECTORY):
        print("❌ DB 폴더가 없습니다. ingest.py를 먼저 실행했나요?")
        return

    # DB 불러오기
    vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # 관련 문서 3개 찾기

    print("🤖 2. Llama(AI)를 준비하는 중...")
    llm = ChatOllama(model="llama3.1", temperature=0)

    # 질문하기
    question = "여권 발급은 어디서 해?"
    print(f"\n❓ 질문: {question}")
    
    # 3. 검색하기 (Retrieve)
    print("🔍 관련 정보를 찾는 중...")
    docs = retriever.invoke(question)
    
    if not docs:
        print("❌ 관련 정보를 찾지 못했습니다.")
        return

    # 찾은 정보를 텍스트로 정리
    context = "\n".join([doc.page_content for doc in docs])
    print(f"📄 참고할 문서 내용(일부):\n{context[:200]}...") # 내용 살짝 보여주기

    # 4. AI에게 시키기 (Prompt)
    # "너는 상담원이야. 아래 [정보]를 보고 질문에 답해." 라고 시킴
    template = """
    당신은 친절한 민원 안내 공무원입니다.
    아래의 [참고 정보]를 바탕으로 질문에 대해 정확하고 친절하게 답변해주세요.
    없는 내용은 지어내지 말고 "정보가 없습니다"라고 하세요.

    [참고 정보]
    {context}

    질문: {question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm

    # 5. 최종 답변 생성
    print("\n💬 AI가 답변을 생성하고 있습니다...")
    response = chain.invoke({"context": context, "question": question})

    print("-" * 30)
    print("✅ 최종 답변:")
    print(response.content)
    print("-" * 30)

if __name__ == "__main__":
    run_rag()