# 구현 소스코드 안내

실제 실행 소스는 이 프로젝트 루트와 mentor/, scripts/, tests/에 포함되어 있다. 문서에 코드 일부만 붙여 넣은 제출물이 아니다. Python 파일 14개는 첨부 원본 starter ZIP과 바이트 단위로 동일하다. 해시 및 비교 결과는 SOURCE_MANIFEST.json을 참조한다.

## 모듈별 역할

| 파일 | 책임 |
|---|---|
| app.py | Streamlit UI, 조건 탐색, 항목 선택, 항목별 대화, 근거 표시, 처리 시간 |
| mentor/__init__.py | 패키지 초기화 |
| mentor/config.py | 환경설정, 경로, TOML 및 JSON 데이터, 예외 |
| mentor/models.py | GMS ChatOpenAI와 로컬/호환 API 임베딩 |
| mentor/collector.py | URL 검증, robots, 원문 수집, 출처 고지, 후보 수집·캐시 |
| mentor/store.py | 두 Chroma 컬렉션, 청킹, 중복 방지, 항목별 검색 |
| mentor/llm.py | 검색어 및 문서 후보 선별, JSON 응답 검사 |
| mentor/pipeline.py | LangGraph 검색·생성, 근거 부족 안내, 인용 번호 검사 |
| mentor/service.py | 조건 기반 탐색 및 도메인 학습 가이드 질문 |
| scripts/build_catalog.py | 항목 메타데이터 생성 |
| scripts/check_setup.py | 비밀 값을 노출하지 않는 설정 검사 |
| scripts/collect_docs.py | 공식 설명문 수집 CLI |
| scripts/index_data.py | 항목 및 원문 초기/재색인 CLI |
| tests/test_core.py | DB 격리·중복·인용·설정·추출·URL 검사 |

## 설정 및 데이터

- requirements.txt: 실행 및 테스트 의존성.
- settings.toml: 청크 900자, 중복 150자, 외부 Top-k 4, 최대 cosine 거리 0.85.
- .env.example: 비밀 키 없는 환경설정 예시. 실제 키는 .env에 입력한다.
- data/items.json: 프로젝트용 직접 작성 메타데이터 112개.
- data/raw: 실제 수집한 설명문 3개. 라이선스·원문 주소·변경 고지를 유지한다.
- .gitignore: 키, 가상환경, 벡터 DB, 모델 파일, 런타임 캐시 제외. 초기 원문 3개는 재현용 입력으로 Git에 포함한다.

## 실행 진입점

README의 설치 → 설정 → 색인 → Streamlit 실행 순서를 따른다. 기존 사용자 프로젝트의 .env와 storage를 이 패키지에 복사해서 배포하지 않는다. 새 환경에서는 모델 다운로드와 색인을 다시 수행한다. 코드 수정본을 사용한다면 문서·해시·검증도 해당 수정본 기준으로 갱신한다.
