#!/usr/bin/env python3
"""
Daily Tech Brief - 카톡 공유 산출물 생성기

입력: data/YYYY-MM-DD.json
출력:
  - Message/YYYY-MM-DD/card.png   (로컬 카톡 첨부 사본)
  - Message/YYYY-MM-DD/text.txt   (로컬 카톡 복붙 텍스트)
  - date/YYYY-MM-DD/og.png        (사이트 OG 이미지, 깃 푸시)

OG 메타가 박힌 일자별 정적 HTML은 build_site.py가 생성한다.

사용법:
    python3 .claude/skills/tech-news-daily/scripts/generate_message.py data/2026-05-26.json
"""
import json
import shutil
import sys
from pathlib import Path

SITE_URL = "https://kaistbiztech.github.io/dailytechbrief/"
PROJECT_ROOT = Path(__file__).resolve().parents[4]   # /Users/cheil/dev/technews
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
KAKAO_TEMPLATE = TEMPLATES_DIR / "kakao-card.html"   # 9:16 세로, 카톡 앱 첨부용
OG_TEMPLATE = TEMPLATES_DIR / "og-card.html"          # 1.91:1 가로, 메신저 OG 미리보기용
MESSAGE_BASE = PROJECT_ROOT / "Message"
DATE_BASE = PROJECT_ROOT / "date"
LOGO_PATH = PROJECT_ROOT / "KCB_Logo.png"


def build_text(edition: dict) -> str:
    """카톡 복붙용 텍스트 — 사이트 링크 상단, KAIST 프레임, 키워드, 3문장 요약."""
    date_str = edition["id"].replace("-", ".")
    dow = edition.get("dayOfWeek", "")
    eid = edition["id"]

    parts = []
    parts.append("📰 KAIST 경영대학 테크 네트워크")
    parts.append("데일리 테크 브리프")
    parts.append(f"{date_str} {dow}요일")
    parts.append("")
    parts.append(f"전체 보기 👉 {SITE_URL}date/{eid}/")

    # 키워드 묶음
    all_kw = []
    for it in edition["newsItems"]:
        all_kw.extend(it.get("keywords", []))
    if all_kw:
        parts.append("")
        parts.append("🔑 오늘의 키워드")
        parts.append(" · ".join(all_kw))

    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("")

    for item in edition["newsItems"]:
        parts.append(f"{item['order']:02d}. {item['title']}")
        parts.append(item["summary"])
        parts.append("")

    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append(f"전체 보기 👉 {SITE_URL}date/{eid}/")
    parts.append("© KAIST 경영대학 테크 네트워크")
    return "\n".join(parts)


def _logo_data_url() -> str | None:
    import base64
    if not LOGO_PATH.is_file():
        return None
    return "data:image/png;base64," + base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")


def _capture(browser, template_path: Path, edition: dict, viewport: dict, out_path: Path, logo_url: str | None) -> None:
    ctx = browser.new_context(viewport=viewport, device_scale_factor=2)
    page = ctx.new_page()
    page.goto(template_path.resolve().as_uri(), wait_until="networkidle")
    page.evaluate(
        "([ed, logo]) => window.renderEdition(ed, logo)",
        [edition, logo_url],
    )
    page.wait_for_timeout(700)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_path), full_page=False, type="png")
    ctx.close()


def generate_cards(edition: dict, kakao_out: Path, og_out: Path) -> None:
    """
    카톡 앱 첨부용 9:16 세로 카드 + 메신저 OG 1.91:1 가로 카드를 각각 캡처.

    - kakao_out: 1080×1920 (Message/<id>/card.png)
    - og_out: 1200×630 (date/<id>/og.png)
    """
    from playwright.sync_api import sync_playwright

    logo_url = _logo_data_url()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        _capture(browser, KAKAO_TEMPLATE, edition,
                 {"width": 1080, "height": 1920}, kakao_out, logo_url)
        _capture(browser, OG_TEMPLATE, edition,
                 {"width": 1200, "height": 630}, og_out, logo_url)
        browser.close()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: generate_message.py <path-to-edition-json>", file=sys.stderr)
        return 1

    json_path = Path(sys.argv[1]).resolve()
    if not json_path.is_file():
        print(f"Not found: {json_path}", file=sys.stderr)
        return 1

    edition = json.loads(json_path.read_text(encoding="utf-8"))
    eid = edition["id"]

    message_dir = MESSAGE_BASE / eid
    message_dir.mkdir(parents=True, exist_ok=True)
    date_dir = DATE_BASE / eid
    date_dir.mkdir(parents=True, exist_ok=True)

    # 1) 텍스트 (로컬)
    text_path = message_dir / "text.txt"
    text_path.write_text(build_text(edition), encoding="utf-8")
    print(f"✓ wrote {text_path.relative_to(PROJECT_ROOT)}")

    # 2) 카드 PNG: 카톡용(9:16) + OG용(1.91:1) 각각 캡처
    card_path = message_dir / "card.png"
    og_path = date_dir / "og.png"
    generate_cards(edition, kakao_out=card_path, og_out=og_path)
    print(f"✓ wrote {card_path.relative_to(PROJECT_ROOT)}")
    print(f"✓ wrote {og_path.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
