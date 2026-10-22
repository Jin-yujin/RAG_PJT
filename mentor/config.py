import json
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class MentorError(Exception):
    """사용자에게 그대로 보여도 되는, 비밀 정보가 없는 오류."""


@dataclass(frozen=True)
class Settings:
    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 4
    max_distance: float = 0.85
    request_interval: float = 1.5
    request_timeout: int = 30
    max_selected_documents: int = 3

    def __post_init__(self):
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise MentorError("chunk_overlap은 0 이상, chunk_size 미만이어야 합니다.")
        if self.chunk_size < 100 or self.top_k < 1:
            raise MentorError("chunk_size는 100 이상, top_k는 1 이상으로 설정하세요.")
        if self.request_interval < 1 or self.request_timeout <= 0:
            raise MentorError("수집 간격은 1초 이상, 제한 시간은 양수로 설정하세요.")
        if self.max_selected_documents < 1:
            raise MentorError("max_selected_documents는 1 이상이어야 합니다.")


def settings():
    try:
        return Settings(**tomllib.loads((ROOT / "settings.toml").read_text("utf-8")))
    except (OSError, ValueError, TypeError) as error:
        raise MentorError("settings.toml의 파일과 설정값을 확인하세요.") from error


def read_json(path, default=None):
    path = Path(path)
    if not path.exists() and default is not None:
        return default
    return json.loads(path.read_text("utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), "utf-8")
    temporary.replace(path)


def catalog():
    items = read_json(ROOT / "data" / "items.json")
    if len({item["id"] for item in items}) != len(items):
        raise MentorError("항목 ID가 중복되어 있습니다.")
    return items
