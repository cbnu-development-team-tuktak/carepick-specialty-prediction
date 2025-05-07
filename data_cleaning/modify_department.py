import json
import os

# 현재 파이썬 파일이 있는 디렉토리 기준으로 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(base_dir, '치과_test.json')
output_file = os.path.join(base_dir, 'output.json')

# JSON 파일 로드
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# department 값을 "산부인과"로 수정
for item in data:
    item['department'] = '치과'

# 수정된 데이터를 저장
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ department 항목이 모두 '산부인과'로 수정되었습니다.")
