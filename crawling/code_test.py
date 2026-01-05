import os
import json
import glob

# ==========================================
# 🛠️ 사용자 설정: 데이터가 있는 최상위 폴더 경로
# (이미지에 보이는 폴더들이 들어있는 그곳!)
# ==========================================
BASE_DIR = 'data/rowdata/'  # 실제 경로로 수정해주세요! (예: C:/Users/Downloads/...)

# 확인하고 싶은 핵심 폴더 후보들 (이미지 보고 골랐습니다)
TARGET_FOLDERS = [
    "법률데이터_법령",
    "법률데이터_생활법령",
    "법령지식_층간소음(Json)",
    "법령지식_교통사고(Json)",
    "TS_법령",  # Training Source (원문) 확인
    "TL_법령_QA"  # Training Label (질문답변) 확인
]


def peek_json_structure(folder_name):
    # 폴더 경로 만들기
    folder_path = os.path.join(BASE_DIR, folder_name)

    # 폴더 안에서 아무 JSON 파일이나 하나 찾기 (하위 폴더 포함)
    json_files = glob.glob(os.path.join(folder_path, '**', '*.json'), recursive=True)

    print(f"\n📂 [폴더 확인]: {folder_name}")

    if not json_files:
        print("   ❌ JSON 파일을 찾을 수 없습니다. (경로가 틀렸거나 압축이 안 풀렸을 수도 있어요)")
        return

    target_file = json_files[0]  # 첫 번째 파일 선택
    print(f"   📄 샘플 파일: {os.path.basename(target_file)}")

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 데이터 구조 맛보기 (최상위 키와 내용 살짝 출력)
        if isinstance(data, dict):
            print(f"   🔑 키(Key) 목록: {list(data.keys())}")
            # 내용 살짝 보여주기 (너무 길면 자름)
            print(f"   👀 내용 미리보기: {str(data)[:300]} ...")
        elif isinstance(data, list):
            print(f"   🔑 리스트 형태입니다. 첫 번째 아이템의 키: {list(data[0].keys()) if data else '비어있음'}")
            print(f"   👀 내용 미리보기: {str(data[0])[:300]} ...")

    except Exception as e:
        print(f"   ⚠️ 읽기 실패: {e}")


def run_inspection():
    print("🚀 데이터 정찰을 시작합니다...")
    for folder in TARGET_FOLDERS:
        peek_json_structure(folder)
    print("\n✅ 정찰 끝! 이 결과를 복사해서 AI에게 보여주세요.")


if __name__ == "__main__":
    run_inspection()