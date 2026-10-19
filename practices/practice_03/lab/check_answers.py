"""Compare saved model answers with the five golden references."""
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GOLD = ROOT / "results" / "golden"
MODEL = ROOT / "results" / "model"


def load(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def check(q: int, text: str) -> list[str]:
    """Return human-readable failures for one saved answer."""
    t = text.lower()
    failures = []
    if "status: ok" not in t:
        failures.append("run status is not OK")

    if q == 1:
        if "make test" not in t:
            failures.append("missing `make test`")
        if "demo/makefile" not in t and "`makefile`" not in t:
            failures.append("missing demo/Makefile source")
    elif q == 2:
        for needle in ("valueerror", "empty name", "service.py"):
            if needle not in t:
                failures.append(f"missing `{needle}`")
    elif q == 3:
        if "unsubscribe" not in t:
            failures.append("missing `unsubscribe`")
        absent = (
            "не реализов",
            "не найден",
            "отсутств",
            "функции нет",
            "нет функции",
        )
        if not any(needle in t for needle in absent):
            failures.append("does not reject the false premise")
    elif q == 4:
        if "ci" not in t:
            failures.append("missing CI reference")
        absent = ("нет ответа", "нет сведений", "не указ", "отсутств", "нет информации")
        reordered_absence = "сведен" in t and "нет" in t
        if not reordered_absence and not any(needle in t for needle in absent):
            failures.append("does not state that CI information is absent")
    elif q == 5:
        lost = ("не сохран", "сбрасыв", "создаётся заново", "создается заново")
        if not any(needle in t for needle in lost):
            failures.append("does not say that subscriptions are lost")
        if "service.py" not in t and "readme.md" not in t:
            failures.append("missing a source file")
    return failures


def main():
    total = 0
    ok = 0
    for i in range(1, 6):
        total += 1
        golden = load(GOLD / f"Q{i}.md").strip()
        model_answer = load(MODEL / f"Q{i}.md")
        failures = check(i, model_answer)
        good = not failures and bool(golden)
        print(f"Q{i}: {'OK' if good else 'FAIL'}")
        print(f"  Golden: {golden or '[missing]'}")
        if failures:
            print(f"  Reasons: {'; '.join(failures)}")
        if not good:
            print("--- Model answer ---")
            print(model_answer)
            print("--------------------")
        ok += int(good)
    print(f"Summary: {ok}/{total} correct")


if __name__ == "__main__":
    main()
