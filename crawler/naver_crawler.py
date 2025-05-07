# 네이버 지식인의 문서 고유번호인 docId를 직접 전수조사하여 크롤링하는 코드
# 쓰레드 기법을 이용하여 병렬 크롤링을 시도하였음
# 현재는 쓰지 않음

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed

# ✅ 대상 진료과 리스트
TARGET_DEPARTMENTS = {
    "심장내과", "내분비내과", "소화기내과", "혈액종양내과", "감염내과", "신장내과", "호흡기내과", 
    "류마티스내과" "이비인후과", "외과", "대장, 항문 외과", "흉부외과", "정형외과", "신경외과",
    "신경과", "정신건강의학과", "성형외과", "피부과", "안과", "비뇨의학과", "산부인과",
    "소아청소년과", "가정의학과", "영상의학과", "마취통증의학과", "재활의학과",
    "응급의학과",
    "충치, 치아질환", "잇몸질환", "치아교정", "의치, 임플란트", "치아 유지, 관리"
}

# ✅ 치과 하위 진료과
DENTAL_SUBFIELDS = {
    "충치, 치아질환", "잇몸질환", "치아교정", "의치, 임플란트", "치아 유지 , 관리"
}

# ✅ 유효 날짜인지 확인
def is_valid_date(date_str):
    try:
        if "전" in date_str:
            return False
        date_obj = datetime.strptime(date_str.strip(), "%Y.%m.%d.")
        return datetime(2024, 1, 1) <= date_obj <= datetime(2024, 12, 31)
    except:
        return False

# ✅ 단일 docId 크롤링 함수
def crawl_doc(doc_id):
    url = f"https://kin.naver.com/qna/detail.naver?d1id=7&dirId=70106&docId={doc_id}"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        tag_list = soup.select_one("div.tagList a")
        actual_department = tag_list.get_text(strip=True) if tag_list else None
        if actual_department not in TARGET_DEPARTMENTS:
            print(f"docId {doc_id}: 진료과 필터링으로 제외됨 → 실제: {actual_department}")
            return None

        department = "치과" if actual_department in DENTAL_SUBFIELDS else actual_department

        title_tag = soup.select_one("div.endTitleSection")
        title = title_tag.get_text(strip=True) if title_tag else None
        if not title:
            return None

        date_spans = soup.select("div.userInfo.userInfo__bullet span")
        date_str = date_spans[2].get_text(strip=True) if len(date_spans) >= 3 else None
        date_str = date_str[3:].strip() if date_str else None

        content_tag = soup.select_one("div.questionDetail")
        content = content_tag.get_text(separator="\n", strip=True) if content_tag else None
        if not content:
            return None

        print(f"docId {doc_id} 저장됨")
        print(f"제목: {title}")
        print(f"작성일: {date_str}")
        print(f"본문: {content[:80]}...")  # 너무 길면 앞 80자만 출력

        return {
            "title": title,
            "content": content,
            "department": department,
            "date": date_str
        }

    except Exception as e:
        print(f"❌ docId {doc_id} 실패: {e}")
        return None
    finally:
        time.sleep(random.uniform(0.2, 0.4))

# ✅ 안전한 wrapper
def safe_crawl(doc_id):
    try:
        return crawl_doc(doc_id)
    except Exception as e:
        print(f"❌ 내부 실패 docId {doc_id}: {e}")
        return None

# ✅ 실행
if __name__ == "__main__":
    print("크롤링 시작")

    start_doc_id = 461390338
    end_doc_id = 461787760
    doc_ids = list(range(start_doc_id, end_doc_id + 1))

    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:  # ✅ Thread 기반
        futures = {executor.submit(safe_crawl, doc_id): doc_id for doc_id in doc_ids}

        for future in as_completed(futures):
            doc_id = futures[future]
            try:
                result = future.result(timeout=8)
                if result:
                    results.append(result)
            except TimeoutError:
                print(f"⏱️ 타임아웃: docId {doc_id}")
            except Exception as e:
                print(f"⚠️ 예외 발생 docId {doc_id}: {e}")

    with open("medical_questions_2024.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 총 {len(results)}건 저장 완료")
