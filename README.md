## Simple typwritting device made with raspberry pi zero W

현대사회는 글을 작성하기 위해 더 이상 펜과 종이를 사용하지 않습니다. 노트북, 핸드폰, 태블릿과 같은 전자 기기들을 이용하여 쉽게 문서를 작성하고 수정하고 저장할 수 있습니다. 하지만 문서의 쉬운 접근만큼 전자 기기에서는 다른 방해 요소들에도 접근이 쉽기에 글쓰기에 집중하기 어려운 환경이 되기 마련입니다. 이번 프로젝트는 우리가 온전히 글쓰기에 집중할 수 있도록 도와주고, 글쓰기에 필요한 요소 외 방해 요소들을 최대한 배제하여 온전히 몰입할 수 있는 환경을 제공하는 제품을 만드는 것에 중점을 두었습니다.

https://www.youtube.com/watch?v=r6y616ogdqU

Z세대, 현재의 20~40대들은 디지털 네이티브 세대, 즉 태어났을 때부터 디지털 환경 속에서 살아왔기 때문에 스마트폰, 태블릿과 같은 기기에 대한 의존도가 괸장히 높다고 한다. 이러한 스마트 기기 의존 생활을 하는 디지털 네이티브 세대 사이에서, 몇년 전부터 [디지털 디톡스]라는 활동이 대두되고 있습니다. 거리낌 없이 스마트 폰으로 사용하는 이 세대조차 현재의 비정상적인 읜존성을 고치고자 의도적으로 디지털 기기를 멀리하는 행동이라고 할 수 있다. 

실제 이러한 디지털 디톡스를 위해 만들어진 라이트 폰, 일명 덤(Dumb)폰은 미국의 Z세대에게 파격적인 인기를 받으며 새로운 스마트 폰 중독이나 디지털 디톡스의 매개체로 활용된 바 있습니다. 단지 이 제품에 그치는게 아니라, 여전히 단단하고 기본적인 2G 폰을 만드는 것으로 유명한 노키아 회사의 영업 이익이 22년 3조원으로 21년보다 20%넘게 증가한 기록만 봐도 이 디지털 디톡스 시장인 마치 다이어트 시장처럼 건강 보조 및 증진의 목적으로 사람들의 머리 속에 자리 잡을 것이라고 봅니다.

## Feature

1. Type writting
2. Import / Export text with USB and Sync Files with Gdrive
3. Ai based text enhancer
4. Ai based web search

# 개발 항목

1. 제품 구조 설계
2. 홈화면
3. 글 작성 화면
4. USB 파일 송수신
5. ai 리터치
6. ai 검색
7. 환경설정(와이파이, 블루투스)

# 개발 로그

## [24.09.21]

### OS 선택

초기 제품의 컨셉은 가볍게 글을 작성할 수 있는 장치를 목표로 하였기에 OS는 GUI를 지원하지 않는 CLI를 사용하기로 결정, 라즈베리파이에서 구동되는 Raspberry Pi OS  Lite를 채택. 

### 문서작성 프로그램 개발

자료조사 결과 curses 라이브러리를 이용한 구현이 많아 해당 방식으로 개발. 커서이동, 엔터, 벡스페이스 문자 삭제, Ctrl + S, + W 와 같은 특수작업들에 대한 처리, 일반 아스키 문자를 입력받으면 화면에 표시되도로 처리. 저장은 fwrite를 이용.

### USB 자동 마운트 문제 해결 시도

USB가 자동으로 마운트 되지 않는 문제가 있는 것을 확인.  

fstab 설정을 하라는 자료를 보고 방법을 찾아보았으나 fstab은 부팅 시 자동 마운트를 설정하는 부분이라 문제 해결에 부적합했음.

다음으로 udev 규칙을 이용한 자동 마운트 설정 방법을 시도.

자동 마운트 스크립트 (/usr/local/bin/mountUSB.sh)

```bash
#!/bin/bash
mkdir -p /mnt/usb
mount -o uid=1000,gid=1000 /dev/disk/by-id/$1 /mnt/usb
```

자동 마운트 해제 스크립트 (/usr/local/bin/unmountUSB.sh)

```bash
#!/bin/bash
umount /mnt/usb
```

스크립트에 실행 권한 부여

```bash
sudo chmod +x /usr/local/bin/mountUSB.sh
sudo chmod +x /usr/local/bin/unmountUSB.sh
```

udev 규칙 파일 생성(/etc/udev/rules.d/99USBMount.rules)

```bash
ACTION=="add", KERNEL=="sd[a-z][0-9]", RUN+="/usr/local/bin/mountUSB.sh %k"
ACTION=="remove", KERNEL=="sd[a-z][0-9]", RUN+="/usr/local/bin/unmountUSB.sh"
```

(udev 규칙 파일명이 99로 시작하는 이유는 숫자에 따라 우선순위가 달라지기 때문.)

udev 서비스 재시작

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

어떠한 이유에서인지 자동 마운트 되지 않음.

## [24.09.22]

### USB 자동 마운트 문제 해결 시도

udisks2를 이용한 USB 자동 마운트 방법 시도

udev 규칙 파일 수정(/etc/udev/rules.d/99USBMount.rules)

```bash
ACTION=="add", KERNEL=="sd[a-z][0-9]", RUN+="/usr/bin/udisksctl mount --block-device /dev/%k"
ACTION=="remove", KERNEL=="sd[a-z][0-9]", RUN+="/usr/bin/udisksctl unmount --block-device /dev/%k"
```

해당 방식으로 사용하면 medai 디렉토리 안에 root사용자로 디렉토리가 생상되고 그 안에 장치가 마운트 되기에 일반 사용자가 접근하지 못하는 문제가 발생함. 권한 문제를 해결하고자 했으나 실패함.

## [24.09.23]

### OS변경

CLI에서는 USB 자동 마운트가 되지 않는다고 판단. 혹여나 Desktop 및 기타 소프트웨어가 설치된 Raspberry Pi OS Full에서는 CLI 부팅에서도 USB가 자동 마운트 될지 궁금하여 해당 방식으로 수행. GUI 환경에서는 자동으로 USB가 마운트 되나, CLI 환경에서는 지원되지 않음. 결국 필수 소프트웨어만 설치돤 Raspberry Pi OS에서 GUI환경을 OS를 설정, 부팅과 함께 파이썬 스크립트가 실행되고 전체 화면을 만드는 것으로 대체하기로 결정함.

### USB 팝업 삭제

Raspberry Pi OS에서 USB를 설치했을 때 장치를 이용한 작업을 선택하기 위한 팝업이 뜨는 현상이 발생. 이를 해결하기 위해 OS의 파일매니저에서 작업을 수행.

**메뉴 → 편집 → 설정 → 미디어 또는 장치 탭 → 팝업 및 자동 옵션 비활성화**

## [24.09.24]

### 문서작성 프로그램 테스트 및 수정

문서 작성 프로그램을 시험해 본 결과, 한글이 입력되지 않는 다는 것을 확인.

SSH 환경에서도 입력되지 않는 것을 확인 하여 라즈베리파이에 한글 입력기가 설치되지 않음과 별개로 한글 입력이 파이썬 프로그램 상에서 지원되지 않는 것이라 판단.  ASCII 문자 입력 부분을 수정하였으나 여전히 한글이 입력되지 않아 문서 작성 기능을 다시 만들기로 결정.

shutil과 keyboard라이브러리를 이용한 텍스트 편집 기능을 구혔하였으나, 글자를 입력할 때마다 화면이 업데이트 되며 블링크 되는 현상과, 커서 위치를 구현하는 기능을 수행하는 복잡도로 해당 방식도 적절하지 않다고 판다.

결과적으로  파이썬 프로그램 중간에 vim을 호출하여 텍스트 에디터 기능을 구현하도록 결정. 그러기 위해 본 프로그램에서 필요치 않은 vim기능은 제거, 추가적으로 필요한 커맨드를 추가해야 한다고 판다.

vim의 단축키를 비활성화 하기 위해서는 vimrc파일을 수정해야 함. 

```
" =========================
" 기본 단축키 비활성화 및 커스터마이징
" =========================

" 기본 명령어 비활성화
nnoremap <silent> : <Nop>
nnoremap <silent> q <Nop>
nnoremap <silent> w <Nop>
nnoremap <silent> x <Nop>
nnoremap <silent> dd <Nop>
nnoremap <silent> yy <Nop>
nnoremap <silent> p <Nop>
nnoremap <silent> u <Nop>
nnoremap <silent> d <Nop>
nnoremap <silent> y <Nop>
nnoremap <silent> r <Nop>

" 화살표로만 커서 이동 가능 (다른 이동 명령어 비활성화)
nnoremap h <Nop>
nnoremap j <Nop>
nnoremap k <Nop>
nnoremap l <Nop>

" 커서 이동을 위한 화살표 방향키만 허용
nnoremap <Up> k
nnoremap <Down> j
nnoremap <Left> h
nnoremap <Right> l

" 편집: 알파벳이나 숫자 입력 시 입력 모드로 전환 (특정 단축키 제외)
nnoremap a i
nnoremap b i
nnoremap c i
nnoremap d i
nnoremap e i
nnoremap f i
nnoremap g i
nnoremap h i
nnoremap i i
nnoremap j i
nnoremap k i
nnoremap l i
nnoremap m i
nnoremap n i
nnoremap o i
nnoremap p i
nnoremap q i
nnoremap r i
nnoremap s i
nnoremap t i
nnoremap u i
nnoremap v i
nnoremap w i
nnoremap x i
nnoremap y i
nnoremap z i

nnoremap 1 i
nnoremap 2 i
nnoremap 3 i
nnoremap 4 i
nnoremap 5 i
nnoremap 6 i
nnoremap 7 i
nnoremap 8 i
nnoremap 9 i
nnoremap 0 i

" 특수 명령어 (Ctrl + S, Ctrl + W, Ctrl + X)를 우회하여 작동하도록 설정
nnoremap <C-s> :w<CR>
nnoremap <C-w> :q<CR>
nnoremap <C-x> :q!<CR>

" 입력 모드에서 Esc로 일반 모드로 돌아가기
inoremap <Esc> <Esc>

" 그 외 모든 기능 비활성화
nnoremap g <Nop>
nnoremap zz <Nop>
nnoremap ZQ <Nop>
nnoremap ZW <Nop>
nnoremap ZZ <Nop>

" ~ 표시 비활성화 (빈 줄에 나타나는 표시)
set fillchars+=eob:\

" =========================
" 상태 표시줄에 항상 메시지 표시
set statusline=명령모드\ :\ Esc\ \|\ 저장\ :\ Ctrl\ +\ S\ \|\ 종료\ :\ Ctrl\ +\ W
set laststatus=2 " 항상 상태줄 표시

" search 명령어를 /home/alpha/search.py로 매핑 (인자 지원)
command! -nargs=* Search execute '!python /home/alpha/search.py ' . <q-args>
```

nmap으로 Ctrl + S, Ctrl + W, Ctrl + X를 구현하면 위의 입력 모드 진입 설정에 먹히기 때문에 입력 모드 전환 규칙을 우회하도록 nnoremap으로 설정 해야한다.

## [24.09.25]

### AI 기능들을 위한 적절한 AI 탐색

AI검색과 리터치 작업을 할 ai들을 선별하는 과정에서 적절한 파이썬 api를 선택해야하기에 다음과 같은 조건에 맞는 것들을 선택하기로 함.

1. 무료인가?
2. 답변속도가 빠른가?
3. 사용하기 간편한가?
4. 변수(리스크)가 없는가?

다음은 해당 조건들을 기반으로 찾은 결과이다.

**groq api**

https://youtu.be/VmNhDUKMHd4?si=nyTbMaz0DmrrMZhc

groq에서 제공하는 Llama 3 모델을 무료로 사용할 수 있음

속도는 빠르나, 한국어가 미숙한 모습을 보임

**GPT4FREE**

https://github.com/xtekky/gpt4free

[gpt4free](https://pypi.org/project/gpt4free/)

gpt를 포함한 다양한 모델들을 우회하여 무료로 사용할 수 있는 있음

정식적인 방식이 아니기에 안정성에 문제가 있음

모델별, Provider별 속도차이가 존재함

-제공 모델 확인 코드

```python
import g4f

def print_available_models():
    # provider가 제공하는 모델 리스트 가져오기
    models = g4f.models._all_models  # 리스트를 직접 사용
    
    # 모델 출력
    for model in models:
        print(model)

if __name__ == "__main__":
    print_available_models()
```

-특정 모델을 사용하여 질문하고, provider와 모델, 답변을 받는 코드

```python
import g4f
from g4f.client import Client

prompt = input(">> ")

client = Client()

chat_completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
)

# 결과 출력
response_content = chat_completion.choices[0].message.content or ""
model = chat_completion.model  # model 정보
provider = chat_completion.provider if hasattr(chat_completion, 'provider') else "N/A"  # provider 정보

print(f"Provider: {provider}")
print(f"Model: {model}")
print(f"Response: {response_content}")
```

gpt-4o : 단일 provider, 속도 약간 느림

gpt-4o-mini : 2개 provider, 속도 약간 느림

gemini-pro : 단일 provider, 속도 빠름, 정확도 낮음

claude-3-haiku : 단일 provider, 속도 빠름, 정체성에 혼란이 있고 비윤리적인 일에 답변을 안 해줌

## [24.09.26]

### AI 검색 기능 구현

**1차 아이디어** : 인자로 받은 검색어를 구글에 검색하여 나오는 상위 5개의 글에 get 요청을 보내 html 코드를 받아온 뒤, 해당 사이트의 p태그 내용을 추출하여 ai에게 요약을 요청하는 방식 → 해당 방식은 구글에서 광고를 포함한 5개의 글을 받아오기 때문에 광고성 글들이 포함 된 정보가 제공될 수 있으며, p태그 내용만을 추출하는 것은 정보를 받아오는 것에 한계가 있다고 판단(나무위키는 p태그가 아님) 해당 방식에서는 googlesearch-python이라는 라이브러리를 사용했음.

**2차 아이디어** : ai 검색을 제공하는 사이트를 탐색. iask.ai라는 사이트를 발견. 뤼튼ai 처럼 ai 검색을 제공하여 간단하게 압축된 정보를 제공. 뤼튼과는 다르게 cloudflare 인증이 없어 get요청으로 html을 받아올 수 있고, 주소에 검색어를 삽입해서 검색이 가능함. → 해당 방식은 iask.ai가 비동기 방식으로 페이지를 구성하기 때문에 단순히 requests 라이브러리를 이용해서는 정보가 담긴 페이지를 받아올 수 없었음. 이를 해결하기 위해서는 selenium라이브러리와 chromium-browser, chromedriver 가 필요한데, 현재 라즈베리파이 제로에서는 chromium이 더 이상 지원되지 않음(성능 이슈로 지원 중단)

**3차 아이디어** : 검색어에 대해 사전에 지정된 특정 사이트들에서 get 요청으로 코드를 받아와 정보를 가공한 뒤, 이를 ai를 통해 요약해줌. 사전에 지정된 사이트라 하면, 나무위키, 네이버, 구글, 구글 뉴스의 첫 번쨰 결과물을 의미함.

플로우는 다음과 같음.

1. 검색어를 입력받음
2. ai에게 해당 검색어에 대한 내용을 물어보고 결과를 저장해둠 → prompt : [검색어]에 대해 알려줘
3. 구글에 site: namu.wiki [검색어]로 검색하여 가장 최상단에 있는 사이트 주소 받아오기(namu.wiki에 관련된 위키로 접속)
4. 받아온 나무위키 주소를 크롤링하여 ai에게 요약을 요청함.
5. [https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=ALL&orderBy=sim&keyword=](https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=ALL&orderBy=sim&keyword=mrbeast%20pdf)[검색어]로 검색하여 가장 최상단에 있는 네이버 블로그 주소 받아오기.
6. 받아온 네이버 블로그를 크롤링하여 ai에게 요약을 요청함.
7. [https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query=](https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query=mrbeast)[검색어]로 검색하여 첫 뉴스 기사 주소 받아오기.
8. 받아온 뉴스 기사를 크롤링하여 ai에게 요약을 요청함
9. 구글에 해당 검색어로 검색하여 나오는 결과들 중 광고, 나무위키, wiki를 제외한 첫번째 글 주소 받아오기.
10. 받아온 주소를 크롤링하여 전체 코드를 받아와 ai에게 요약을 요청함.
11. 여태까지 요약되고 저장된 모든 내용들을 각각의 다음과 같이 출력
[검색어]에 대한 검색 결과 입니다.
[AI] : 
[나무위키] : (나무위키 요약 내용)
[네이버] : (네이버 블로그 요약 내용)
[뉴스 기사] : (뉴스 기사 요약 내용)
[구글] : (구글에서 나온 사이트 요약 내용)

크롤링 및 a요약은 다음 코드를 참고한다.

```python
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate

# 네이버 뉴스기사 주소
url = 'https://n.news.naver.com/article/437/0000361628?cds=news_media_pc'

# 웹 문서 크롤링
loader = WebBaseLoader(url)

# 뉴스기사의 본문을 Chunk 단위로 쪼갬
text_splitter = CharacterTextSplitter(        
    separator="\n\n",
    chunk_size=3000,     # 쪼개는 글자수
    chunk_overlap=300,   # 오버랩 글자수
    length_function=len,
    is_separator_regex=False,
)

# 웹사이트 내용 크롤링 후 Chunk 단위로 분할
docs = WebBaseLoader(url).load_and_split(text_splitter)

# 각 Chunk 단위의 템플릿
template = '''다음의 내용을 한글로 요약해줘:

{text}
'''

# 전체 문서(혹은 전체 Chunk)에 대한 지시(instruct) 정의
combine_template = '''{text}

요약의 결과는 다음의 형식으로 작성해줘:
제목: 신문기사의 제목
주요내용: 한 줄로 요약된 내용
작성자: 김철수 대리
내용: 주요내용을 불렛포인트 형식으로 작성
'''

# 템플릿 생성
prompt = PromptTemplate(template=template, input_variables=['text'])
combine_prompt = PromptTemplate(template=combine_template, input_variables=['text'])

# LLM 객체 생성
llm = ChatOpenAI(temperature=0, 
                 model_name='gpt-3.5-turbo-16k')

# 요약을 도와주는 load_summarize_chain
chain = load_summarize_chain(llm, 
                             map_prompt=prompt, 
                             combine_prompt=combine_prompt, 
                             chain_type="map_reduce", 
                             verbose=False)
```

실행환경이 chromium을 포함한 어떠한 브라우저도 설치 되지 않은 라즈베리파이 제로 환경이라는 것을 인지하며, 모든 ai 관련된 기능은 다음 코드를 참고한다.

```python
import g4f
from g4f.client import Client

prompt = input("[prompt]>> ")

client = Client()

chat_completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
)

# 결과 출력
response_content = chat_completion.choices[0].message.content or ""
print(f"Response: {response_content}")
```

## [24.09.27]

### AI 검색 기능 구현

**4차 아이디어** : 기사를 갖고 오는 과정에서 5000자가 넘으면 ai가 처리하는 한도가 넘어간다는 문제를 발견, 기사를 청크 단위로 나눈 뒤 요약 후, 요약본을 결합하는 방식으로 플로우를 수정. 검색 증간 생성(RAG) 방식으로 개발하는 것을 목표로 코드를 작성. ai는 g4f가 하루 한계가 있고 속도가 느리다는 단점이 있어 groq api를 이용하고 결정. groq에서 제공하는 모델들 중 gemma2가 한국어 처리가 잘 되기에 해당 모델을 이용한 개발로 결정.

```python
import os
import re
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from langchain.text_splitter import CharacterTextSplitter
from groq import Groq

# Groq API 클라이언트 설정
client = Groq(api_key="...")

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
```
