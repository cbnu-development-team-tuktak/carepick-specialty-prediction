import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import calendar
import time
import json
import os

QUERY = "안녕하세요"
BASE_URL = "https://kin.naver.com/search/list.nhn"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_POSTS_PER_MONTH = 7000
MAX_PAGE = 100
CRAWL_MONTH = 1
OUTPUT_DIR = "./train_data"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def is_valid_date(date_str, start_dt, end_dt):
    try:
        if "전" in date_str:
            return False
        date_obj = datetime.strptime(date_str.strip().rstrip("."), "%Y.%m.%d")
        return start_dt.date() <= date_obj.date() <= end_dt.date()
    except Exception as e:
        print(f"⚠️ 날짜 파싱 실패: '{date_str}' -> {e}")
        return False


def extract_department(profile_url):
    try:
        res = requests.get(profile_url, headers=HEADERS, timeout=3)
        if res.status_code != 200:
            return "ERROR"
        soup = BeautifulSoup(res.text, "html.parser")
        profile_section = soup.select_one("div.my_doctor div.my_personal_inner div.profile_section2 div.pro_intro dl.pro_name dd span")
        if not profile_section:
            return "ERROR"
        raw_text = profile_section.get_text(strip=True)
        if "치과의사" in raw_text:
            return "치과"
        department = raw_text.replace("전문의", "").strip()
        return department
    except Exception as e:
        print(f"❌ 프로필 페이지 오류: {profile_url} -> {e}")
        return "ERROR"
    
def extract_doctor_name(profile_url):
    try:
        res = requests.get(profile_url, headers=HEADERS, timeout=3)
        if res.status_code != 200:
            return "ERROR"
        soup = BeautifulSoup(res.text, "html.parser")
        profile_section = soup.select_one("div.my_doctor div.my_personal_inner div.profile_section2 div.pro_intro dl > dt")
        if not profile_section:
            print("의사 이름 추출 실패: 선택자 불일치")
            return "ERROR"
        doctor_name = profile_section.get_text(strip=True)
        return doctor_name
    except Exception as e:
        print(f"❌ 의사 이름 추출 중 오류 발생: {profile_url} -> {e}")
        return "ERROR"
    except Exception as e:
        print(f"❌ 프로필 페이지 오류: {profile_url} -> {e}")
        return "ERROR"


def save_to_file(data, department):
    if department == "":
        filename = os.path.join(OUTPUT_DIR, f"미분류_train.json")
    else:
        filename = os.path.join(OUTPUT_DIR, f"{department}_train.json")
        
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.append(data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)


def get_detail_content(url, start_dt, end_dt):
    try:
        
        print(url)
        res = requests.get(url, headers=HEADERS, timeout=3)
        if res.status_code != 200:
            return "ERROR"

        soup = BeautifulSoup(res.text, "html.parser")
        date_spans = soup.select("div.userInfo.userInfo__bullet span")
        if not date_spans:
            return "ERROR"
        
        if len(date_spans) == 4:
            date_str_raw = date_spans[2].get_text(strip=True)
        elif len(date_spans) == 3:
            date_str_raw = date_spans[1].get_text(strip=True)
        else:
            return "ERROR"
        
        if date_str_raw.startswith("끌올작성일"):
            date_str_raw = date_str_raw.replace("끌올작성일", "").strip()

        if date_str_raw.startswith("작성일"):
            date_str_raw = date_str_raw.replace("작성일", "").strip()

        if not is_valid_date(date_str_raw, start_dt, end_dt):
            return "OUT_OF_RANGE"
        
        title_tag = soup.select_one("div.endTitleSection")
        title = title_tag.get_text(strip=True).replace("질문", "").strip() if title_tag else None
        content_tag = soup.select_one("div.questionDetail")
        content = content_tag.get_text(separator="\n", strip=True) if content_tag else None
        
        # 여러 개의 답변 블록(_contentBox contentBox)을 모두 확인
        content_boxes = soup.select("div._contentBox.contentBox")
        expert_found = False
        profile_url = None

        for box in content_boxes:
            expert_badge = box.select_one("div.profile_card._profileCardArea div.card_info div.profile_info div.badge_area span.badge.expert_job")
            if expert_badge and expert_badge.get_text(strip=True) == "전문의":
                link_tag = box.select_one("div.profile_card._profileCardArea a[href]")
                if link_tag:
                    profile_url = link_tag.get("href")
                    expert_found = True
                    break  # 하나만 찾으면 충분하므로 중단

        if not expert_found or not profile_url:
            return "ERROR"

        if not profile_url.startswith("http"):
            profile_url = f"https://kin.naver.com{profile_url}"
        
        profile_link_tag = soup.select_one("div._contentBox div.profile_card._profileCardArea a[href]")
        
        if not profile_link_tag:
            return "ERROR"
        
        profile_url = profile_link_tag.get("href")
        if not profile_url.startswith("http"):
            profile_url = f"https://kin.naver.com{profile_url}"
            
        
        department = extract_department(profile_url)
        if department == "ERROR":
            print("진료과 추출 에러")
            return "ERROR"
        
        doctor_name = extract_doctor_name(profile_url)
        if doctor_name == "ERROR":
            print("의사명 추출 에러")
            return "ERROR"

        data = {
            "title": title,
            "content": content,
            "department": department,
            "date": date_str_raw,
            "question_url": url,
            "answer_url": profile_url,
            "doctor": doctor_name
        }
        print(data["title"])
        save_to_file(data, department)

        return data

    except Exception as e:
        print(f"❌ 상세 페이지 오류: {url} -> {e}")
        return "ERROR"


def crawl_month(year, month):
    start_dt = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_dt = datetime(year, month, last_day)
    
    total_results = []

    # 하루 단위로 범위 분할
    current_start = start_dt
    while current_start <= end_dt:
        
        if len(total_results) >= MAX_POSTS_PER_MONTH:
            break
        
        current_end = min(current_start + timedelta(days=0), end_dt)
        period_str = f"{current_start.strftime('%Y.%m.%d.')}|{current_end.strftime('%Y.%m.%d.')}"
        print(f"🗓️ {period_str} 수집 중...")
        
        page = 1
        
        while len(total_results) < MAX_POSTS_PER_MONTH and page <= MAX_PAGE:
            params = {
                "sort": "date",
                "query": QUERY, 
                "period": period_str,
                "section": "qna",
                "dirId": 701,
                "page": page
            }

            try:
                res = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=3)
                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.select("ul.basic1 > li")
                if not items:
                    break
                
                print(f"{page}번째 페이지 조회중...")

                for item in items:
                    a_tag = item.select_one("dl dt > a")
                    href = a_tag.get("href") if a_tag else None
                    if href:
                        detail_url = href if href.startswith("http") else f"https://kin.naver.com{href}"
                        result = get_detail_content(detail_url, current_start, current_end)
                        
                        if result not in ["OUT_OF_RANGE", "ERROR"]:
                            total_results.append(result)

                page += 1
                time.sleep(0.3)

            except Exception as e:
                print(f"❌ 페이지 요청 오류: {e}")
                break
        
        # 다음 범위로 이동
        current_start = current_end + timedelta(days=1)
        page = 1
        time.sleep(0.3)

    return total_results

if __name__ == "__main__":
    # print(f"\n======= 수집 시작 =======")
    # for month in range(1, 4):
    #     crawl_month(2025, month)
    #     time.sleep(1)

    #     print(f"\n✅{month}월 데이터 수집 완료")
        
    total = 0
    for file in os.listdir(OUTPUT_DIR):
            if file.endswith(".json"):
                with open(os.path.join(OUTPUT_DIR, file), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        total += len(data)
                        print(f"{file}의 데이터 개수 {len(data)}개, {len(data) / 25212 * 100}%")
                    except Exception as e:
                        print(f"⚠️ 파일 로딩 오류: {file} -> {e}")

    print(f"✅총 저장된 질문 수: {total}건")