import pandas as pd
import json
import os
import glob
from tqdm import tqdm  # 진행바 표시 라이브러리 (없으면 pip install tqdm)

# ==========================================
# 🛠️ 사용자 설정 (경로를 본인 환경에 맞게 꼭 수정하세요!)
# ==========================================
# 1. 원본 데이터 폴더 경로
TS_FOLDER = 'data/rowdata/TS_법령/'  # CSV 파일들이 있는 곳 (법전)
TL_FOLDER = 'data/rowdata/TL_법령_QA/'  # JSON 파일들이 있는 곳 (Q&A)

# 2. 결과물 저장 경로
OUTPUT_DIR = 'data/processed/'
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================

def process_law_textbook():
    """
    [TS 데이터 처리]
    법령 CSV 파일들을 모아서 AI가 검색할 '법전(DB)'을 만듭니다.
    핵심 컬럼: '내용' (제1조 목적...)
    """
    print(f"\n📚 1. 법령 교과서(Context) 만드는 중... ({TS_FOLDER})")
    csv_files = glob.glob(os.path.join(TS_FOLDER, '**', '*.csv'), recursive=True)

    if not csv_files:
        print("   ❌ CSV 파일이 없습니다. 경로를 확인해주세요!")
        return

    all_laws = []

    for file in tqdm(csv_files, desc="CSV 병합 중"):
        try:
            # 인코딩 문제 해결 (utf-8-sig 또는 cp949 시도)
            try:
                df = pd.read_csv(file, encoding='utf-8-sig')
            except:
                df = pd.read_csv(file, encoding='cp949')

            # 필요한 컬럼만 추출 ('내용' 컬럼이 핵심!)
            if '내용' in df.columns:
                # '내용' 컬럼을 가져오되, 데이터프레임 형태로 변환
                temp_df = df[['내용']].copy()

                # (선택) 법령일련번호가 있으면 같이 가져와도 좋음
                if '법령일련번호' in df.columns:
                    temp_df['source_id'] = df['법령일련번호']

                all_laws.append(temp_df)

        except Exception as e:
            print(f"   ⚠️ 파일 에러 ({os.path.basename(file)}): {e}")

    if all_laws:
        final_df = pd.concat(all_laws, ignore_index=True)

        # 데이터 정제 (빈 칸 제거)
        final_df = final_df.dropna(subset=['내용'])
        final_df = final_df[final_df['내용'].str.strip() != ""]

        save_path = os.path.join(OUTPUT_DIR, 'law_database.csv')
        final_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"   ✅ [성공] 법령 데이터 {len(final_df)}개 저장 완료! -> {save_path}")
    else:
        print("   ⚠️ 저장할 데이터가 없습니다.")


def process_law_qa():
    """
    [TL 데이터 처리]
    QA JSON 파일들을 모아서 AI 학습/테스트용 '기출문제집'을 만듭니다.
    핵심 키: label -> input(질문), output(답변)
    """
    print(f"\n📝 2. 기출문제집(Q&A) 만드는 중... ({TL_FOLDER})")
    json_files = glob.glob(os.path.join(TL_FOLDER, '**', '*.json'), recursive=True)

    if not json_files:
        print("   ❌ JSON 파일이 없습니다. 경로를 확인해주세요!")
        return

    qa_list = []

    for file in tqdm(json_files, desc="JSON 파싱 중"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # label 키 안에 있는 input(질문), output(답변) 추출
            if 'label' in data:
                question = data['label'].get('input', '').strip()
                answer = data['label'].get('output', '').strip()

                if question and answer:
                    qa_list.append({
                        'question': question,
                        'answer': answer,
                        'filename': os.path.basename(file)  # 출처 확인용
                    })

        except Exception as e:
            # 파일이 너무 많으면 에러 로그는 생략하거나 파일에 기록하는 게 좋음
            pass

    if qa_list:
        final_df = pd.DataFrame(qa_list)
        save_path = os.path.join(OUTPUT_DIR, 'law_qa.csv')
        final_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"   ✅ [성공] Q&A 데이터 {len(final_df)}세트 저장 완료! -> {save_path}")
    else:
        print("   ⚠️ 저장할 Q&A 데이터가 없습니다.")


if __name__ == "__main__":
    # 라이브러리 설치 안내 (혹시 없을까봐)
    # pip install pandas tqdm

    process_law_textbook()
    process_law_qa()