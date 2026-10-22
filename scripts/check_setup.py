"""비밀 값을 출력하지 않고 설정과 패키지만 확인합니다."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mentor.config import catalog, settings
from mentor.models import chat_ready

print("Python:", sys.version.split()[0])
print("항목 메타데이터:", len(catalog()))
print("GMS 설정:", "세 항목 입력됨(실제 연결은 미검증)" if chat_ready() else "미입력: 검색·색인 준비는 가능, AI 답변은 설정 필요")
print("청크 설정:", settings())
for package in ["streamlit", "chromadb", "langgraph", "sentence_transformers"]:
    print(package, "설치됨" if importlib.util.find_spec(package) else "설치 필요")
