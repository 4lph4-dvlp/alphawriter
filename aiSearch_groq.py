import os
import re
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from langchain.text_splitter import CharacterTextSplitter
from groq import Groq

# Groq API 클라이언트 설정
client = Groq(api_key="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")

# 특수문자 삭제 및 불필요한 줄바꿈 제거 함수
def clean_summary(text):
    # @#$%^&*~`와 같은 특수문자 삭제
    text = re.sub(r"[#@\$%^&*~`]", "", text)
    
    # 두 개 이상의 줄바꿈을 하나로 줄임
    text = re.sub(r"\n{2,}", "\n", text)
    
    # 앞뒤 불필요한 공백 제거
    return text.strip()

# AI 요약 함수
def summarize_text(text_chunk, prompt):
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "user",
                "content": prompt + text_chunk
            },
        ],
        temperature=1,
        max_tokens=4500,
        top_p=1,
        stream=False,
        stop=None,
    )
    return completion.choices[0].message.content or ""

# 웹페이지 크롤링 및 본문 요약
def crawl_and_summarize(url, content_selector):
    try:
        print(f"[*] 페이지({url})의 정보를 받아옵니다...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 지정된 셀렉터에서 본문 추출
        content = soup.select_one(content_selector)
        if content:
            full_text = content.get_text(separator="\n").strip()

            # 4000자 초과 시 청크로 분할
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=4000,
                chunk_overlap=0,
                length_function=len,
                is_separator_regex=False,
            )
            docs = text_splitter.split_text(full_text)

            # 각 Chunk에 대해 AI 요약 수행
            summaries = []
            total_chunks = len(docs)

            for idx, doc in enumerate(docs):
                percentage = (idx + 1) / total_chunks * 100
                print(f"[*] AI 요약 중... {percentage:.2f}%")
                summary = summarize_text(doc, "다음 내용을 한글로 요약해줘:\n\n")
                summaries.append(summary)

            # 전체 요약 결과를 조합
            final_summary = "\n\n".join(summaries)

            # 최종 요약이 2000자를 넘는 경우 1000자로 다시 요약
            if len(final_summary) > 2000:
                print("[*] 최종 요약이 2000자를 초과하여 1000자로 요약합니다.")
                if len(final_summary) > 4000:
                    # 4000자씩 청크로 나눠서 요약
                    docs = text_splitter.split_text(final_summary)
                    summaries = []
                    total_chunks = len(docs)

                    for idx, doc in enumerate(docs):
                        percentage = (idx + 1) / total_chunks * 100
                        print(f"[*] AI 요약 중... {percentage:.2f}%")
                        summary = summarize_text(doc, "다음 내용을 1000자로 요약해줘:\n\n")
                        summaries.append(summary)
                    final_summary = "\n\n".join(summaries)
                else:
                    final_summary = summarize_text(final_summary, "다음 내용을 1000자로 요약해줘:\n\n")

            # 요약 결과 후처리 (특수문자 제거 및 줄바꿈 정리)
            return clean_summary(final_summary)
        else:
            print("[!] 본문을 찾지 못했습니다.")
            return ""

    except Exception as e:
        print(f"[!] 오류 발생: {e}")
        return ""

# 나무위키 링크 검색
def get_namu_wiki_link(search_query):
    query = f"site:namu.wiki {search_query}"
    print(f"[*] 나무위키에서 '{search_query}'에 대한 링크를 검색합니다...")
    results = list(search(query, num_results=1))
    return results[0] if results else None

# 구글 검색에서 위키, 나무위키, 광고 제외한 첫 번째 사이트 링크 가져오기
def get_google_search_result(query):
    print(f"[*] 구글에서 '{query}'에 대한 링크를 검색합니다...")

    # 필터링할 사이트들
    exclude_keywords = ['namu.wiki', 'wikipedia.org', 'wiki', 'ads.google.com']

    # 5개의 검색 결과를 가져온 후 필터링
    results = list(search(query, num_results=5))

    # 필터링하여 첫 번째 적절한 결과 반환
    for result in results:
        if not any(keyword in result for keyword in exclude_keywords):
            return result

    print("[!] 적절한 검색 결과를 찾을 수 없습니다.")
    return None

# 구글 뉴스 링크 가져오기 (뉴스 필터링)
def get_google_news_result(query):
    print(f"[*] 구글에서 '{query}'에 대한 뉴스 링크를 검색합니다...")
    news_query = f"{query} news"
    results = list(search(news_query, num_results=5))

    if results:
        return results[0]  # 첫 번째 뉴스 링크 반환
    else:
        print("[!] 관련 뉴스 링크를 찾을 수 없습니다.")
        return None

# 네이버 뉴스 검색
def get_naver_news_link(search_query):
    print(f"[*] 네이버에서 '{search_query}'에 대한 뉴스 링크를 검색합니다...")
    naver_news_url = f"https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query={search_query}"
    response = requests.get(naver_news_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_link = soup.select_one('a.news_tit')
    return news_link['href'] if news_link else None

# 메인 프로그램
def main():
    search_query = input("검색어를 입력하세요: ")

    # AI에게 검색어에 대한 정보 요청
    print("[*] AI에게 물어보는 중...")
    ai_info = summarize_text("", f"[{search_query}]에 대해 자세히 알려줘.")
    ai_info = clean_summary(ai_info)  # 요약 후 처리

    # 나무위키 링크 가져오기
    namu_wiki_link = get_namu_wiki_link(search_query)
    namu_summary = crawl_and_summarize(namu_wiki_link, 'div.D8VwlnF6.snJO-KHa') if namu_wiki_link else "[!] 나무위키 링크를 찾을 수 없습니다."

    # 구글 뉴스 링크 가져오기
    google_news_link = get_google_news_result(search_query)
    google_news_summary = crawl_and_summarize(google_news_link, 'body') if google_news_link else "[!] 뉴스 링크를 찾을 수 없습니다."

    # 네이버 뉴스 링크 가져오기
    naver_news_link = get_naver_news_link(search_query)
    naver_news_summary = crawl_and_summarize(naver_news_link, 'body') if naver_news_link else "[!] 뉴스 링크를 찾을 수 없습니다."

    # 구글 검색 링크 가져오기
    google_link = get_google_search_result(search_query)
    google_summary = crawl_and_summarize(google_link, 'body') if google_link else "[!] 구글 링크를 찾을 수 없습니다."

    # 결과 출력 전 화면 초기화
    os.system('cls' if os.name == 'nt' else 'clear')

    # 최종 결과 출력
    print("\n{}에 대한 검색 결과입니다.".format(search_query))
    print("[AI] :", ai_info)
    print("\n\n==============================\n\n")
    print("[나무위키] :", namu_summary)
    print("\n\n==============================\n\n")
    print("[뉴스1] :", google_news_summary)
    print("\n\n==============================\n\n")
    print("[뉴스2] :", naver_news_summary)
    print("\n\n==============================\n\n")
    print("[구글] :", google_summary)
    
if __name__ == "__main__":
    main()