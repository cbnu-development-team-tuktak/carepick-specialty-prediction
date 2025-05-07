import os
import json

# ✅ 수정할 디렉토리 경로 지정
INPUT_DIR = "./train_data"  # ← 여기에 실제 경로 입력

# ✅ 디렉토리 내 모든 JSON 파일 처리
for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".json"):
        continue

    file_path = os.path.join(INPUT_DIR, filename)
    
    # 🔸 파일 로딩
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ JSON 디코딩 실패: {filename}")
            continue

    # 🔸 각 항목에서 줄바꿈 제거
    modified = False
    for item in data:
        if "title" in item:
            new_title = item["title"].replace("\n", " ")
            if new_title != item["title"]:
                item["title"] = new_title
                modified = True
        if "content" in item:
            new_content = item["content"].replace("\n", " ")
            if new_content != item["content"]:
                item["content"] = new_content
                modified = True

    # 🔸 변경이 있을 경우 덮어쓰기
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 수정 완료: {filename}")
    else:
        print(f"☑️ 변경 없음: {filename}")
