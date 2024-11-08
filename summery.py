import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
import g4f
from g4f.client import Client

# 네이버 뉴스기사 URL
url = 'https://namu.wiki/w/%EC%9C%A4%EC%84%9D%EC%97%B4'

# 웹 페이지 HTML 소스 가져오기
print("[*] 페이지의 정보를 받아옵니다...")
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 본문 추출
print("[*] 필요한 정보를 추출합니다...")
content = soup.find('div', {'class': 'D8VwlnF6 snJO-KHa'})

# 추출된 본문이 존재하는지 확인
if content:
    content = content.get_text(strip=True)
else:
    print("[!] 본문을 찾지 못했습니다.")
    content = ""

# 크롤링한 내용이 있을 경우에만 진행
if content:
    # 본문에 줄바꿈 강제로 추가 (테스트)
    content = content.replace(".", ".\n\n")
    
    # 뉴스 기사의 본문을 4000자 단위로 쪼갬
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=4000,     # 쪼개는 글자수
        chunk_overlap=0,     # 오버랩 제거
        length_function=len,
        is_separator_regex=False,
    )

    # 문서를 Chunk 단위로 분할
    docs = text_splitter.split_text(content)

    # 각 Chunk 단위로 AI에게 요약 요청
    client = Client()

    def summarize_text(prompt):
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        
        # 결과를 반환
        response_content = chat_completion.choices[0].message.content or ""
        return response_content

    # 각 Chunk에 대해 요약 수행
    summaries = []
    total_chunks = len(docs)  # 총 청크 수

    for idx, doc in enumerate(docs):
        percentage = (idx + 1) / total_chunks * 100  # 퍼센트 계산
        print(f"[*] AI 요약 중... {percentage:.2f}%")
        prompt = f"다음의 내용을 한글로 요약해줘:\n\n{doc}"
        summary = summarize_text(prompt)
        summaries.append(summary)

# 전체 요약 결과를 조합
final_summary = "\n\n".join(summaries)

# 최종 요약이 2000자를 넘는 경우 1000자로 다시 요약
if len(final_summary) > 2000:
    print("[*] 최종 요약이 2000자를 초과하여 1000자로 요약합니다.")
    prompt = f"다음의 내용을 1000자 이내로 요약해줘:\n\n{final_summary}"
    final_summary = summarize_text(prompt)

# 최종 결과 출력
print("요약이 완료되었습니다.")
print(final_summary)
