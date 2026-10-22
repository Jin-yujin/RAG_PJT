"""메타데이터 112건과 저장된 공식 문서를 색인합니다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mentor.config import MentorError, ROOT, catalog, read_json
from mentor.store import Store


def main():
    store = Store()
    items = catalog()
    print("메타데이터 임베딩 중... 첫 실행에는 모델 다운로드가 필요합니다.")
    print("메타데이터 색인:", store.index_items(items))
    raw = ROOT / "data" / "raw"
    count = 0
    lookup = {item["url"]: item for item in items}
    for path in sorted(raw.glob("*.json")):
        document = read_json(path)
        item = lookup.get(document["url"])
        if item:
            store.index_document(item, document)
            count += 1
    print("저장된 공식 문서:", count, "외부 문서 청크:", store.docs.count())
    print("완료: python -m streamlit run app.py")


if __name__ == "__main__":
    try:
        main()
    except MentorError as error:
        print(str(error))
        sys.exit(1)
    except Exception:
        print("색인에 실패했습니다. 패키지 설치, 모델 다운로드 네트워크와 저장 공간을 확인하세요.")
        sys.exit(1)
