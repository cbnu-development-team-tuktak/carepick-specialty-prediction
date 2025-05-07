# 네이버 지식인의 문서 고유번호인 docId를 직접 전수조사하여 크롤링하는 코드
# 현재는 쓰지 않음

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

start_doc_id = 461390338
end_doc_id = 461390438
# end_doc_id = 479810814
dir_id = 70106  # 정형외과
output_data = []

TARGET_DEPARTMENTS = {"내과", "이비인후과", "외과", "대장, 항문 외과", "흉부외과", "정형외과", "신경외과", 
                      "신경과", "정신건강의학과", "성형외과", "피부과", "안과", "비뇨의학과", "산부인과",
                      "소아청소년과", "암센터", "가정의학과", "영상의학과", "마취통증의학과", "재활의학과",
                      "응급의학과", "종합병원", "요양병원", "핵의학과", "충치, 치아질환", "잇몸질환", "치아교정", "의치, 임플란트", "치아 유지 , 관리"}  # 필요한 진료과 추가

DENTAL_SUBFIELDS = {
    "충치, 치아질환", "잇몸질환", "치아교정", "의치, 임플란트", "치아 유지 , 관리"
}

# 날짜 필터 함수
def is_valid_date(date_str):
    try:
        if "전" in date_str:  # "26분 전", "1시간 전" 등의 상대 표현은 제외
            return False
        date_obj = datetime.strptime(date_str.strip(), "%Y.%m.%d.")
        return datetime(2024, 1, 1) <= date_obj <= datetime(2024, 12, 31)
    except:
        return False

print("크롤링 시작")

for doc_id in range(start_doc_id, end_doc_id + 1):
    print(f"docId {doc_id} 요청 중...")
    
    url = f"https://kin.naver.com/qna/detail.naver?d1id=7&dirId=70106&docId={doc_id}"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
        if res.status_code != 200:
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        
        # 진료과 확인 (tagList 내부 첫 번째 a 태그)
        tag_list = soup.select_one("div.tagList a")
        actual_department = tag_list.get_text(strip=True) if tag_list else None

        if actual_department not in TARGET_DEPARTMENTS:
            print(f"docId {doc_id}: 진료과 필터링으로 제외됨 → 실제: {actual_department}")
            continue
          
        # 진료과 통합 처리
        if actual_department in DENTAL_SUBFIELDS:
            department = "치과"
        else:
            department = actual_department  # 그대로 사용

        # 제목
        title_tag = soup.select_one("div.endTitleSection")
        title = title_tag.get_text(strip=True) if title_tag else None
        if not title:
            continue
        
        # 작성일: userInfo__bullet > 세 번째 span
        date_spans = soup.select("div.userInfo.userInfo__bullet span")
        date_str = date_spans[2].get_text(strip=True) if len(date_spans) >= 3 else None
        date_str = date_str[3:].strip() 
        # if not date_str or not is_valid_date(date_str):
        #     print(f"docId {doc_id}: 작성일 없음 (비공개 또는 삭제글일 가능성)")
        

        # 본문 내용
        content_tag = soup.select_one("div.questionDetail")
        content = content_tag.get_text(separator="\n", strip=True) if content_tag else None
        if not content:
            continue

        output_data.append({
            "title": title,
            "content": content,
            "department": department,  # 실제 진료과로 저장
            "date": date_str
        })

        print(f"docId {doc_id} 저장됨")
        print(f"제목: {title}")
        print(f"작성일: {date_str}")
        print(f"본문: {content[:80]}...")  # 너무 길면 앞 80자만 출력
        time.sleep(0.2)

    except Exception as e:
        print(f"docId {doc_id} 실패: {e}")
        continue

# JSON 저장
with open("orthopedics_2024.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n총 {len(output_data)}건 저장 완료")