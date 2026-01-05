import pandas as pd
import json
import os
import glob

# ==========================================
# 🛠️ 사용자 설정 (파일 경로를 실제 위치로 수정하세요!)
# ==========================================
# 1. TS (CSV) 파일들이 있는 폴더 경로
TS_FOLDER_PATH = 'data/rowdata/TS_법령/'

# 2. 법령지식 (JSON) 파일들이 있는 폴더 경로
KNOWLEDGE_FOLDER_PATH = 'data/rowdata/법령지식_층간소음(Json)/'

# 3. 결과 저장 경로
OUTPUT_DIR = 'data/processed/'
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================

def process_ts_csv(folder_path):
    print(f"\n📊 [TS 데이터] CSV 파일 처리 시작: {folder_path}")
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    if not csv_files:
        print("   ❌ CSV 파일이 없습니다. 경로를 확인해주세요.")
        return

    # 샘플로 첫 번째 파일만 열어서 컬럼을 확인해봅니다.
    # (실제로는 모든 파일을 합쳐야 하지만, 일단 구조 확인부터!)
    sample_file = csv_files[0]
    try:
        # csv파일이 한글이라 깨지면 encoding='cp949' 또는 'euc-kr'로 바꿔보세요
        df = pd.read_csv(sample_file, encoding='utf-8-sig')
        print(f"   📄 파일명: {os.path.basename(sample_file)}")
        print(f"   🔑 컬럼 목록: {list(df.columns)}")
        print("   👀 데이터 미리보기 (상위 3개):")
        print(df.head(3))

        # TODO: 여기서 필요한 컬럼만 남기고 저장하는 코드로 발전시킬 예정

    except Exception as e:
        print(f"   ⚠️ 읽기 실패: {e}")


def process_knowledge_json(folder_path):
    print(f"\n🧠 [법령지식] JSON 파일 처리 시작: {folder_path}")
    json_files = glob.glob(os.path.join(folder_path, '*.json'))

    if not json_files:
        print("   ❌ JSON 파일이 없습니다.")
        return

    extracted_data = []

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 법령지식 데이터는 보통 이런 구조일 가능성이 높습니다.
            # (구조가 다르면 출력된 키를 보고 수정해야 합니다)
            # 예: {'info': {...}, 'questions': [...]}

            # 일단 전체 데이터를 평평하게 펴거나, Q&A를 찾습니다.
            # 여기서는 데이터의 '키(Key)'를 확인하기 위해 샘플만 출력합니다.
            if len(extracted_data) == 0:
                print(f"   📄 샘플 파일: {os.path.basename(file_path)}")
                print(f"   🔑 최상위 키: {list(data.keys())}")

            # 만약 'question'이나 'answer' 같은 키가 있다면 추출
            # (아직 구조를 모르니 일단 Pass)

        except Exception as e:
            print(f"   ⚠️ 오류 발생: {file_path} - {e}")


if __name__ == "__main__":
    # 1. TS CSV 확인
    process_ts_csv(TS_FOLDER_PATH)

    # 2. 법령지식 JSON 확인
    process_knowledge_json(KNOWLEDGE_FOLDER_PATH)