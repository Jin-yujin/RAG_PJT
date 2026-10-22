# 출처와 이용 조건

## 직접 작성한 데이터

data/items.json은 학습 항목 이름·분류·수준·짧은 소개를 프로젝트용으로 직접 작성한 목록입니다.
공식 문서의 본문이나 공식 제공 API 데이터 112건을 내려받았다고 주장하지 않습니다.
소개 수준도 공식 난이도 등급이 아니라 이 프로젝트의 학습 분류입니다.

## Android 공식 문서

- 출처: https://developer.android.com/
- 정책: https://developer.android.com/license
- 공식 정책은 문서의 기본 라이선스를 Apache 2.0으로 안내하며 개별 예외를 우선합니다. 비문서 콘텐츠는 CC BY 2.5로 구분합니다.
- 수집기에서 개별 페이지에 CC BY 링크가 확인되면 그 링크를 기록하고, 없으면 문서 기본 정책과 그 판단 근거를 기록합니다.
- Apache 2.0 전문: docs/APACHE-2.0.txt. 원문: https://www.apache.org/licenses/LICENSE-2.0
- 코드·이미지·동영상은 수집에서 제외. 설명 본문의 저작권 문구는 보존하고 발견한 고지 문구도 notices에 보관합니다.
- java.*, javax.*, android.icu.*, org.* 참조 문서는 별도 조건을 검토하기 전까지 URL 검증에서 제외합니다.
- 링크만으로 라이선스를 판단하는 자동화에는 한계가 있습니다. 외부 공개 전에 수집 문서의 개별 예외·저작권 고지·NOTICE를 확인하세요.
- 앱은 Google의 공식 서비스가 아니며 Google/Android 로고를 사용하지 않습니다.

제공된 원문 JSON은 실제 수집 시각, 원문 주소, 제공자, 이용 조건, 변경 사항을 포함합니다.
본문은 사이트 설명 텍스트의 발췌·변환본입니다. 검색 결과와 AI 답변에는 해당 출처를 표시합니다.

## 로컬 임베딩 모델

- 이름: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- 출처: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- 제공: Sentence Transformers
- 모델 카드 라이선스: Apache-2.0.
- 모델 파일은 ZIP에 포함하지 않으며 첫 색인 때 해당 제공처에서 다운로드합니다.

## 애플리케이션과 타사 라이브러리

requirements.txt의 라이브러리는 각 프로젝트의 라이선스를 따릅니다. 앱을 외부 배포하거나 바이너리로 재배포할 때는 포함되는 의존성의 고지도 정리하세요.
GMS는 사용자가 발급받은 키와 사용 가능한 모델을 사용하며 GMS/API 제공자의 이용 조건도 별도로 적용됩니다.
