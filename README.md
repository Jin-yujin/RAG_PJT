# Android 개발 문서 RAG 멘토

Android 공식 문서를 참고해 질문에 답하고 출처를 제시하는 비공식 학습 서비스입니다.
직접 작성한 학습 항목 메타데이터 112건과 실제 수집한 공식 문서 3건을 시작 자료로 제공합니다.
전체 112개 항목의 공식 본문을 모두 수집·검증한 상태는 아닙니다.

## 제출물 안내

| 번호 | 제출물 | 위치 |
|---|---|---|
| 1 | 요구사항 정의서 | [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) |
| 2 | RAG 파이프라인 설계문서 | [docs/PIPELINE.md](docs/PIPELINE.md) |
| 3 | 검증 결과 | [docs/VERIFICATION.md](docs/VERIFICATION.md) |
| 4 | 구현 소스코드 | app.py, mentor/, scripts/, tests/ 및 [구성 설명](docs/SOURCE_CODE.md) |
| 5 | 셀프 체크리스트 | [docs/SELF_CHECKLIST.md](docs/SELF_CHECKLIST.md) |
| 6 | README | 이 파일 |

추가 자료: [GitLab 업로드 방법](docs/GITLAB_UPLOAD.md), [출처와 이용 조건](docs/SOURCES.md).

이 제출본은 사용자가 다시 선택한 원본 starter 기반이다. Python 구현 파일은 원본과 동일하고 문서·.gitignore·예제 환경설정만 보완했다. 화면 서식 수정본과 자동 서식 갱신 기능은 포함하지 않는다. 이미 실행 중인 프로젝트가 있다면 먼저 백업하고 실제 소스가 이 버전과 같은지 확인한다. 실행 중인 파일이 다르면 덮어쓰지 말고 문서의 구현 설명을 실제 버전에 맞춰 수정한다.

검증 기록에는 이번 패키지 검사와 원본의 과거 실행 기록이 구분되어 있다. 실제 GMS 답변·시간·화면 증거는 실행 후 기입해야 한다.

## 처음 실행하기: Windows + VS Code

### 1. 압축 풀기

압축 안의 android-rag-mentor 폴더 내용물을 현재 만든 빈 android-rag-mentor 폴더 안에 복사하세요.
VS Code 왼쪽 탐색기에 app.py, requirements.txt, mentor, scripts, data가 바로 보여야 합니다.
android-rag-mentor/android-rag-mentor/app.py처럼 한 단계 중첩되지 않게 주의하세요.

### 2. Python 확인

VS Code 상단 Terminal → New Terminal. 다음 명령은 Windows PowerShell 기준입니다.

```powershell
py --version
```

이 프로젝트는 tomllib 사용 때문에 Python 3.11 이상이 필요합니다. Python 3.12를 권장합니다.
Python이 없으면 https://www.python.org/downloads/ 에서 설치하세요.
VS Code 확장 메뉴에서 Microsoft의 Python 확장도 설치하세요.

### 3. 가상환경과 의존성

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

CPU 전용 PyTorch를 먼저 설치하면 이 예제에 필요 없는 GPU 패키지 설치를 줄일 수 있습니다.
설치에는 시간이 걸릴 수 있습니다. 첫 색인에서는 다국어 임베딩 모델도 다운로드합니다.

Ctrl+Shift+P → Python: Select Interpreter → .venv의 Python을 선택하세요.
위 명령은 가상환경의 실행 파일을 직접 사용하므로 Activate.ps1이나 실행 정책 변경이 필요 없습니다.

### 4. GMS 설정

```powershell
Copy-Item .env.example .env
```

VS Code에서 .env를 열고 세 값을 입력하세요.

```dotenv
GMS_API_KEY=발급받은_실제_키
GMS_BASE_URL=https://gms.ssafy.io/gmsapi/api.openai.com/v1/
GMS_MODEL=gpt-5.4-nano
```

키 자리는 본인 키로 바꿔야 합니다. 주소와 모델은 사용자가 제공한 실습 코드 기준이며 계정에서 사용 가능한 설정인지 확인하세요. GMS 안내 https://gms.ssafy.io/web/ 의 OpenAI 호환 호출 예제를 확인하세요.
기본 주소에 /chat/completions까지 붙이지 않습니다. 실제 기본 주소 형식은 GMS 안내를 따릅니다.
지원하지 않는 임의의 모델 이름을 넣지 마세요. 키를 채팅·README·Git에 올리지 마세요.

EMBEDDING_PROVIDER=local과 EMBEDDING_MODEL은 우선 그대로 둡니다.
임베딩은 PC에서 계산하고 답변·검색어 추출·후보 선별·조건 선별만 GMS를 사용합니다.
따라서 GMS가 임베딩 API를 제공하지 않아도 로컬 임베딩 방식으로 사용할 수 있습니다.
이 구현은 OpenAI 호환 Chat Completions를 가정합니다. GMS의 다른 제공자 전용 API는 어댑터 변경이 필요합니다.

### 5. 설정 점검과 색인

```powershell
.\.venv\Scripts\python.exe scripts/check_setup.py
.\.venv\Scripts\python.exe scripts/index_data.py
```

색인은 ‘문서를 벡터로 바꿔 검색할 수 있게 저장’하는 작업입니다.
처음에는 Hugging Face 모델 다운로드 때문에 오래 걸릴 수 있습니다. 다음 실행부터 저장된 모델을 사용합니다.
GMS 키 없이도 로컬 색인은 가능합니다. 별도 Hugging Face 키는 공개 모델 다운로드에 필수는 아닙니다.
모델 다운로드 사이트가 막힌 환경이면 허용된 네트워크에서 모델을 받거나 사용할 수 있는 임베딩 API로 설정을 바꾸세요.

### 6. 화면 실행

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

브라우저 http://localhost:8501 에서 열립니다. VS Code의 파일 실행 ▶ 버튼이 아닌 위 명령을 사용합니다.
종료는 터미널에서 Ctrl+C입니다.

### 7. 첫 질문

1. ‘선택 항목 질문’ 탭을 선택합니다.
2. 왼쪽에서 ‘앱 서명’을 고릅니다.
3. ‘질문 전에 관련 문서 수집’은 처음에는 꺼 둡니다.
4. ‘업로드 키와 앱 서명 키는 어떻게 달라?’라고 질문합니다.
5. 답변의 [근거 N]과 아래 원문·출처를 확인합니다.
6. ‘근거 기반 학습 가이드 만들기’도 눌러 봅니다.

처음 포함한 공식 문서는 앱 서명, 앱 아키텍처, Compose 상태 관리 3건입니다.
다른 항목을 고르면 먼저 ‘현재 항목 공식 문서 수집·색인’ 버튼을 누르세요.
‘질문 전에 관련 문서 수집’을 켜면 검색어 추출과 후보 선별 프롬프트도 사용합니다.
이때 여러 번의 GMS 호출과 문서 수집이 발생하므로 답변 시간·사용량이 늘어납니다.

### 8. 조건 검색

‘조건으로 항목 찾기’ 탭에서 예를 들어 ‘로컬 데이터 저장을 배우고 싶어’라고 검색합니다.
메타데이터 의미 검색 → GMS 조건 선별 → 후보 카드 → ‘이 항목 선택’ → 질문 탭 순서입니다.
후보가 없으면 없다고 안내합니다. 모델 선별의 정확성은 대표 조건으로 직접 평가해야 합니다.

## 데이터 수집을 확장하려면

공식 사이트를 수집할 수 있는 환경에서 실행하세요.

```powershell
.\.venv\Scripts\python.exe scripts/collect_docs.py --limit 12
.\.venv\Scripts\python.exe scripts/index_data.py
```

전체 허용 목록을 수집하려면 --limit 112를 사용합니다. 112건 모두 정상 URL·정상 본문이라고 미리 보장하지 않습니다.
성공/실패는 data/collection_report.json에 저장하며 실패를 성공으로 집계하지 않습니다.
원문이 이미 있으면 재다운로드하지 않습니다. 수집 요청 간격·재시도·robots.txt를 적용합니다.
항목 메타데이터를 수정하면 색인 스크립트를 다시 실행하세요.

## 검색 설정

settings.toml에서 chunk_size, chunk_overlap, top_k, max_distance를 변경합니다.
청킹 설정을 바꿨다면 scripts/index_data.py를 다시 실행하세요.
top_k는 외부 문서 근거 수입니다. 선택한 항목 메타데이터는 추가로 항상 포함됩니다.
모델의 최대 입력 길이보다 긴 청크는 임베딩 시 일부가 잘릴 수 있으므로 실제 질문으로 설정을 평가하세요.

## 파일 구성

| 파일 | 역할 |
|---|---|
| app.py | Streamlit 화면, 항목 선택, 세션별 채팅, 상태 안내 |
| mentor/config.py | 설정, 데이터 경로, JSON 읽기·저장 |
| mentor/models.py | GMS ChatOpenAI, 로컬/원격 임베딩 |
| mentor/llm.py | 검색어 추출·후보 선별 프롬프트와 JSON 파싱 |
| mentor/collector.py | 허용 목록 원문 수집, 이용 조건 기록, 캐시 |
| mentor/store.py | Chroma 두 컬렉션, 청킹, 임베딩, 색인, 검색 |
| mentor/pipeline.py | LangGraph retrieve/generate와 인용 번호 검사 |
| mentor/service.py | 조건 탐색과 학습 가이드 |
| data/items.json | 직접 작성한 112개 항목 메타데이터 |
| data/raw/*.json | 실제 수집한 공식 설명 텍스트와 출처 |
| scripts/collect_docs.py | 원문 수집 명령 |
| scripts/index_data.py | 초기 색인·재색인 명령 |
| docs/REQUIREMENTS.md | 요구사항 대응표와 미완료 범위 |
| docs/PIPELINE.md | 파이프라인 설계 |
| docs/SOURCES.md | 출처·이용 조건 |
| docs/VERIFICATION.md | 실제 검증과 사용자 확인 항목 |

## 테스트

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

자동 테스트는 API 키 없이 실행합니다. 테스트용 임베딩은 DB 격리·중복 검사용이며 실제 의미 검색 품질을 검증하지 않습니다.
GMS의 실제 응답 정확성·인용의 사실적 타당성·사용자 PC 속도는 별도로 확인하세요.

## 자주 발생하는 문제

- No module named ...: .venv의 Python으로 requirements.txt를 설치했는지 확인.
- py를 찾지 못함: Python 설치 후 VS Code를 다시 열기. 설치된 python 명령이 있다면 py 대신 python 사용.
- GMS 오류: 실제 기본 주소·모델 ID·키 권한·한도 확인. 키 원문을 공유하지 않기.
- 모델 다운로드 실패: Hugging Face와 모델 파일 제공처 접속 확인. 프록시 환경에서 socksio가 없다는 오류면 python -m pip install "httpx[socks]" 실행.
- 검색된 공식 문서가 없음: 선택한 항목 원문을 수집하고 색인. 필요하면 검색 거리·청크 설정을 평가.
- API 항목인데 Compose 기능이 나오지 않음: 플랫폼 API 목록과 Jetpack/Compose 학습 주제는 다른 항목이므로 관련 학습 주제를 선택.
- 100건이 보이는데 외부 문서가 3개임: 정상입니다. 항목 메타데이터 건수와 실제 수집한 원문 건수는 서로 다릅니다.
- 라이브러리 버전: 이 구현은 명세의 모든 정확한 버전을 고정한 배포가 아닙니다. requirements.txt와 검증 기록을 확인하세요.

## 현재 범위

심화 기능 F2013~F2016은 포함하지 않았습니다.
F2004는 고정 공식 문서 허용 목록 안의 후보 검색으로 부분 대응하며 전체 사이트 검색 API는 구현하지 않았습니다.
대화 기록은 항목별로 분리하지만 브라우저 세션 종료 후 영구 저장하지 않습니다.
공식 문서 이용 조건과 모델 라이선스는 docs/SOURCES.md에 정리했습니다.


## GitLab / GitHub 제출

ZIP 자체만 올리는 대신 압축을 푼 소스와 docs를 Git으로 올린다. 루트에서 README.md와 app.py가 바로 보여야 한다. .env, .venv, storage는 제외한다. 상세 절차는 docs/GITLAB_UPLOAD.md를 따른다. 이후 GitHub는 별도 원격 저장소로 연결할 수 있다.

## 사용 기술 및 재현 범위

Python 3.12 / Streamlit / LangChain / LangGraph / Chroma / Sentence Transformers / GMS OpenAI 호환 Chat Completions를 사용한다. requirements.txt는 허용 버전 범위를 사용하며 모든 의존성이 고정된 잠금 파일은 아니다. 원본 실행 버전 기록은 docs/TESTED_VERSIONS.json에 있지만, 현재 환경 재설치가 그 버전과 동일하다는 의미는 아니다.
