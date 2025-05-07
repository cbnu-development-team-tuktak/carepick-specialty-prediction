# pykospacing을 활용하여 띄어쓰기를 올바르게 수정하는 코드
# 오히려 띄어쓰기가 이상해지는 부분이 있어서 현재는 사용하지 않음

import os
import json
from pykospacing import Spacing

# ✅ 띄어쓰기 보정기 초기화
spacing = Spacing()

# ✅ 보정 함수
def correct_text(text):
    try:
        return spacing(text)
    except Exception as e:
        print(f"⚠️ 보정 실패: {e}")
        return text  # 실패 시 원문 유지

# ✅ 디렉토리 내 모든 JSON 파일에 적용
def correct_json_files_in_dir(directory):
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(directory, filename)
        print(f"📂 처리 중: {filename}")

        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"❌ JSON 파싱 실패: {filename}")
                continue

        modified = False
        for item in data:
            if "title" in item:
                new_title = correct_text(item["title"])
                if new_title != item["title"]:
                    item["title"] = new_title
                    modified = True

            if "content" in item:
                new_content = correct_text(item["content"])
                if new_content != item["content"]:
                    item["content"] = new_content
                    modified = True

        if modified:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 보정 및 저장 완료: {filename}")
        else:
            print(f"☑️ 변경 없음: {filename}")

# ✅ 실행
if __name__ == "__main__":
    DATA_DIR = "./train_data"  # ← 여기를 실제 경로로 수정
    correct_json_files_in_dir(DATA_DIR)
