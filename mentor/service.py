from mentor.llm import json_call


def explore(store, condition):
    candidates = store.search_items(condition)
    if not candidates:
        return []
    result = json_call(
        "당신은 Android 학습 항목 추천 담당자입니다. 자연어 조건을 충족하는 후보만 고르세요. "
        "후보의 필드에서 확인되지 않는 조건은 추측하지 말고 제외하세요. "
        '형식: {"matches":[{"id":"후보 id", "reason":"조건에 맞는 이유"}]}',
        {"condition": condition, "candidates": candidates},
    )
    matches = result.get("matches", [])
    if not isinstance(matches, list):
        return []
    lookup = {item["id"]: item for item in candidates}
    rows, seen = [], set()
    for match in matches:
        if not isinstance(match, dict):
            continue
        identifier = match.get("id")
        if isinstance(identifier, str) and identifier in lookup and identifier not in seen:
            seen.add(identifier)
            rows.append({"item": lookup[identifier], "reason": str(match.get("reason", ""))})
    return rows


def learning_question(item):
    return (f"{item['name']}을 처음 학습하는 Android 개발자를 위한 학습 가이드를 만들어 줘. "
            "공식 문서에서 확인되는 역할, 핵심 개념, 적용할 때 확인할 사항을 순서대로 설명해 줘. "
            "각 설명에 근거를 붙이고 문서에 없는 내용은 확인되지 않는다고 밝혀 줘.")
