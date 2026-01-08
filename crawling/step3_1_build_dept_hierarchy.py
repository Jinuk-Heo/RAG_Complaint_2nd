import pandas as pd
import psycopg2
import glob
import os
from tqdm import tqdm

# DB 접속 정보
DB_CONFIG = { "host": "localhost", "database": "complaint_db", "user": "postgres", "password": "0000", "port": "5432" }

def get_or_create_dept(cursor, name, category, parent_id=None):
    """
    부서가 있으면 ID를 반환하고, 없으면 새로 만들고 ID를 반환하는 함수
    """
    if parent_id:
        cursor.execute("SELECT id FROM departments WHERE name = %s AND category = %s AND parent_id = %s", (name, category, parent_id))
    else:
        cursor.execute("SELECT id FROM departments WHERE name = %s AND category = %s AND parent_id IS NULL", (name, category))
        
    res = cursor.fetchone()
    if res:
        return res[0]

    try:
        cursor.execute("""
            INSERT INTO departments (name, category, parent_id, is_active) 
            VALUES (%s, %s, %s, true) 
            RETURNING id
        """, (name, category, parent_id))
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"   [!] 생성 오류 ({name}): {e}")
        return None

def build_hierarchy():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # [수정 포인트] 진욱 님이 말씀하신 processed_data 폴더를 가장 먼저 확인합니다.
    target_path = "data/processed_data/*.csv"
    file_list = glob.glob(target_path) 
    
    # 만약 위 폴더가 비어있다면 기존 폴더들도 후보로 둡니다.
    if not file_list:
        file_list = glob.glob("data/step1_output/*.csv") + glob.glob("data/*.csv")

    # 중복 제거 (혹시 같은 파일이 여러 경로에 있을 경우 대비)
    file_list = list(set(file_list))

    print(f"[*] 총 {len(file_list)}개의 파일에서 조직 정보를 추출합니다.")
    if len(file_list) == 0:
        print("[!] 파일을 찾을 수 없습니다. 경로를 다시 확인해주세요.")
        return

    for file_path in file_list:
        filename = os.path.basename(file_path)
        # 파일명에서 '구' 이름 추출 (예: 강동구_xxx.csv -> 강동구)
        gu_name = filename.split('_')[0] 

        if "구" not in gu_name: 
            continue

        print(f"\n[*] 처리 중: {gu_name}")

        gu_id = get_or_create_dept(cursor, gu_name, 'GU', None)
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='cp949', errors='ignore')

        if 'resp_dept' not in df.columns:
            print(f"   [!] {filename}: resp_dept 컬럼이 없습니다. 건너뜀.")
            continue

        unique_depts = df['resp_dept'].dropna().unique()

        for dept_str in tqdm(unique_depts, desc=f"{gu_name} 부서 등록"):
            dept_str = str(dept_str).strip()
            if not dept_str: continue

            parts = dept_str.split()

            if len(parts) >= 2:
                guk_name = parts[0]
                gwa_name = " ".join(parts[1:])
                guk_id = get_or_create_dept(cursor, guk_name, 'GUK', gu_id)
                get_or_create_dept(cursor, gwa_name, 'GWA', guk_id)

            elif len(parts) == 1:
                gwa_name = parts[0]
                get_or_create_dept(cursor, gwa_name, 'GWA', gu_id)

    # 기본값 등록
    cursor.execute("INSERT INTO departments (name, category) VALUES ('정보없음', 'NONE') ON CONFLICT DO NOTHING")

    conn.commit()
    conn.close()
    print("\n[+] 조직도 계층화 구축 완료!")

if __name__ == "__main__":
    build_hierarchy()