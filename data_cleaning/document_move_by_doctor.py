import json















DOCTOR = "소성민"
DEPARTMENT = "비뇨의학과"

# 파일 경로
source_file = "./test_data/미분류_test.json"
target_file = f"./test_data/{DEPARTMENT}_test.json"

# 1. 내과 데이터 로드
with open(source_file, "r", encoding="utf-8") as f:
    naegwa_data = json.load(f)

# 2. 조건에 맞는 문서 분리
moved_data = [item for item in naegwa_data if item.get("doctor") == DOCTOR]
remaining_data = [item for item in naegwa_data if item.get("doctor") != DOCTOR]

# 3. 기존 내과 파일 덮어쓰기 (지정된 의사 문서 제거)
with open(source_file, "w", encoding="utf-8") as f:
    json.dump(remaining_data, f, ensure_ascii=False, indent=2)

# 4. 기존 소화기내과 파일이 있다면 불러오고 없으면 빈 리스트
try:
    with open(target_file, "r", encoding="utf-8") as f:
        target_data = json.load(f)
except FileNotFoundError:
    target_data = []

# 5. 이동 대상 데이터 추가
target_data.extend(moved_data)

# 6. 소화기내과 파일 저장
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(target_data, f, ensure_ascii=False, indent=2)

print(f"{len(moved_data)}개의 문서를 {target_file}으로 이동 완료했습니다.")
