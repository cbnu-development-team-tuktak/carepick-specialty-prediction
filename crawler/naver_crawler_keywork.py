# 네이버 지식인에 "안녕하세요" 키워드를 검색한 후 설정한 기간 동안 작성된 글을 크롤링하는 코드

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
import time
import json

# 진료과 매핑 (dirId)
# 여기에 작성된 진료과에 대해 크롤링을 수행함
DEPARTMENTS = {
    "치과": "702"
}

# 크롤링할 진료과 ID
DIR_ID = "70119" # url을 완성하기 위해 임의로 넣은 진료과
QUERY = "안녕하세요"
BASE_URL = "https://kin.naver.com/search/list.nhn"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_POSTS_PER_MONTH = 333  # 월당 최대 수집 수

def is_valid_date(date_str, start_dt, end_dt):
    try:
        if "전" in date_str:
            return False
        date_obj = datetime.strptime(date_str.strip().rstrip("."), "%Y.%m.%d")
        return start_dt.date() <= date_obj.date() <= end_dt.date()
    except Exception as e:
        print(f"⚠️ 날짜 파싱 실패: '{date_str}' -> {e}")
        return False

def get_detail_content(url, start_dt, end_dt):
    try:
        res = requests.get(url, headers=HEADERS, timeout=2)
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
        title = title_tag.get_text(strip=True) if title_tag else None
        if title and title.startswith("질문"):
            title = title[len("질문"):].strip()

        content_tag = soup.select_one("div.questionDetail")
        content = content_tag.get_text(separator="\n", strip=True) if content_tag else None

        tag_list = soup.select_one("div.tagList a")
        department = tag_list.get_text(strip=True) if tag_list else None

        if not all([title, content, department]):
            return "ERROR"

        return {
            "title": title,
            "content": content,
            "department": department,
            "date": date_str_raw
        }

    except Exception as e:
        print(f"❌ 상세 페이지 오류: {url} -> {e}")
        return "ERROR"

def crawl_month(year, month, dir_id):
    start_dt = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_dt = datetime(year, month, last_day)

    total_results = []
    page = 1

    while len(total_results) < MAX_POSTS_PER_MONTH:
        period_str = f"{start_dt.strftime('%Y.%m.%d.')}|{end_dt.strftime('%Y.%m.%d.')}"
        params = {
            "sort": "date",
            "query": QUERY,
            "period": period_str,
            "section": "qna",
            "dirId": dir_id,
            "page": page
        }
        print(f"{period_str} / page {page} 요청 중...")

        try:
            res = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=3)
        except Exception as e:
            print(f"❌ 페이지 요청 오류: {e}")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("ul.basic1 > li")
        if not items:
            break

        for item in items:
            if len(total_results) >= MAX_POSTS_PER_MONTH:
                break

            a_tag = item.select_one("dl dt > a")
            href = a_tag.get("href") if a_tag else None
            if href:
                detail_url = href if href.startswith("http") else f"https://kin.naver.com{href}"
                result = get_detail_content(detail_url, start_dt, end_dt)

                if result == "OUT_OF_RANGE":
                    return total_results
                elif result == "ERROR":
                    continue
                else:
                    total_results.append(result)

        page += 1
        time.sleep(0.3)

    return total_results

if __name__ == "__main__":
    for dept_name, dir_id in DEPARTMENTS.items():
        all_results = []
        print(f"\n\n======= {dept_name} 수집 시작 =======")
        for month in range(1, 4):
            monthly_results = crawl_month(2025, month, dir_id)
            all_results.extend(monthly_results)
            time.sleep(1)

        filename = f"{dept_name}_test.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"\n✅ {dept_name} 저장 완료: {filename} (총 {len(all_results)}건)\n")

# 테스트 데이터셋을 크롤링할 때 쓸 코드
# def crawl_month(year, month):
#     print(f"\n📅 {year}년 {month}월 크롤링 시작")

#     start_dt = datetime(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_dt = datetime(year, month, last_day)

#     total_results = []
#     page = 1

#     while len(total_results) < MAX_POSTS_PER_MONTH:
#         period_str = f"{start_dt.strftime('%Y.%m.%d.')}|{end_dt.strftime('%Y.%m.%d.')}"
#         params = {
#             "sort": "date",
#             "query": QUERY,
#             "period": period_str,
#             "section": "qna",
#             "dirId": DIR_ID,
#             "page": page
#         }
#         print(f"{period_str} / page {page} 요청 중...")

#         try:
#             res = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=3)
#         except Exception as e:
#             print(f"❌ 페이지 요청 오류: {e}")
#             break

#         soup = BeautifulSoup(res.text, "html.parser")
#         items = soup.select("ul.basic1 > li")
#         if not items:
#             print("게시물 없음: 종료")
#             break

#         for item in items:
#             if len(total_results) >= MAX_POSTS_PER_MONTH:
#                 break

#             dl_tag = item.select_one("dl")
#             a_tag = dl_tag.select_one("dt > a") if dl_tag else None
#             href = a_tag.get("href") if a_tag else None
#             if href:
#                 detail_url = href if href.startswith("http") else f"https://kin.naver.com{href}"
#                 print(detail_url)
#                 result = get_detail_content(detail_url, start_dt, end_dt)

#                 if result == "OUT_OF_RANGE":
#                     print("⛔ 날짜 초과 글 → 다음 구간으로 이동")
#                     return total_results
#                 elif result == "ERROR":
#                     print("⚠️ 오류 발생 → 다음 글로 건너뜀")
#                     continue
#                 else:
#                     total_results.append(result)
#                     print(f"저장: {result['title'][:30]}...")

#         page += 1
#         time.sleep(0.3)

#     filename = f"정형외과_{year}_{str(month).zfill(2)}_qna.json"
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(total_results, f, ensure_ascii=False, indent=2)

#     print(f"\n✅ {filename} 저장 완료 (총 {len(total_results)}건)\n")

# if __name__ == "__main__":
#     crawl_month(2024, 12)