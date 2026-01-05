import pandas as pd

# 파일 경로
INPUT_FILE = 'data/processed/law_database.csv'
OUTPUT_FILE = 'data/processed/law_database_refined.csv'


def refine_database():
    print(f"🧹 데이터 정밀 청소 시작: {INPUT_FILE}")
    try:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')
    except:
        df = pd.read_csv(INPUT_FILE, encoding='cp949')

    original_count = len(df)

    # 1. 길이가 10글자 미만인 행 제거
    # (공백 제거 후 기준)
    df = df[df['내용'].str.strip().str.len() >= 10]

    # 2. 특수문자만 있거나 의미 없는 데이터 필터링 (선택사항)
    # 예: "제1조", "부칙" 등만 달랑 있는 경우 제외하고 싶으면 추가 가능

    deleted_count = original_count - len(df)
    print(f"   - 총 {original_count}개 중 {deleted_count}개의 불량 데이터(10자 미만)를 삭제했습니다.")
    print(f"   - 남은 데이터: {len(df)}개")

    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"✨ 저장 완료: {OUTPUT_FILE}")


if __name__ == "__main__":
    refine_database()

    # 전체 개수 확인용 한 줄 코드
    print(len(pd.read_csv('data/processed/law_database_final.csv')))
    # 결과가 568570 나오면 100% 정상입니다.