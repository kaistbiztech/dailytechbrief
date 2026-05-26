#!/usr/bin/env python3
"""
Daily Tech Brief - 사이트 빌드 스크립트

`index.html` 템플릿에 OG 메타와 라우팅 변수를 박은 일자별 정적 페이지를 생성한다.

- 루트 `index.html`: 최신 호와 동일한 내용 (og:url만 사이트 루트)
- `date/<id>/index.html`: 각 일자별 풀 페이지
- `date/<id>/og.png`: 그 일자 카드 PNG 사본 (메신저 OG 이미지)
   * `Message/<id>/card.png`가 존재하면 거기서 복사

`generate_message.py`가 카드 PNG를 만들고 나서 호출되거나, 단독 실행 가능.

사용법:
    python3 .claude/skills/tech-news-daily/scripts/build_site.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

SITE_URL = "https://kaistbiztech.github.io/dailytechbrief/"
BASE_PATH = "/dailytechbrief/"
PROJECT_ROOT = Path(__file__).resolve().parents[4]   # /Users/cheil/dev/technews
INDEX_HTML = PROJECT_ROOT / "index.html"
DATA_DIR = PROJECT_ROOT / "data"
MESSAGE_DIR = PROJECT_ROOT / "Message"
DATE_DIR = PROJECT_ROOT / "date"

META_PATTERN = re.compile(
    r"<!-- BUILD:META:START -->.*?<!-- BUILD:META:END -->",
    flags=re.DOTALL,
)


def esc(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load_editions() -> list[dict]:
    eds = []
    for f in sorted(DATA_DIR.glob("*.json"), reverse=True):
        try:
            eds.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"skip {f.name}: {e}", file=sys.stderr)
    eds.sort(key=lambda e: e["id"], reverse=True)
    return eds


def build_meta_block(edition: dict, latest_id: str, og_url: str) -> str:
    eid = edition["id"]
    date_str = eid.replace("-", ".")
    dow = edition.get("dayOfWeek", "")
    title = f"데일리 테크 브리프 — {date_str} {dow}요일"
    headlines = " · ".join(
        f'{it["order"]:02d} {it["title"]}' for it in edition.get("newsItems", [])[:3]
    )
    og_image = f"{SITE_URL}date/{eid}/og.png"

    return (
        f"<title>{esc(title)}</title>\n"
        f'<meta property="og:type" content="article">\n'
        f'<meta property="og:title" content="{esc(title)}">\n'
        f'<meta property="og:description" content="{esc(headlines)}">\n'
        f'<meta property="og:image" content="{esc(og_image)}">\n'
        f'<meta property="og:image:width" content="1080">\n'
        f'<meta property="og:image:height" content="1920">\n'
        f'<meta property="og:url" content="{esc(og_url)}">\n'
        f'<meta property="og:site_name" content="KAIST 경영대학 테크 네트워크">\n'
        f'<meta property="og:locale" content="ko_KR">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{esc(title)}">\n'
        f'<meta name="twitter:description" content="{esc(headlines)}">\n'
        f'<meta name="twitter:image" content="{esc(og_image)}">\n'
        f"<script>\n"
        f"  /* BASE_PATH는 페이지 JS의 fallback이 location.pathname에서 도출 */\n"
        f'  window.__INITIAL_ID__ = "{eid}";\n'
        f'  window.__LATEST_ID__ = "{latest_id}";\n'
        f"</script>"
    )


def render_page(template_html: str, edition: dict, latest_id: str, og_url: str) -> str:
    meta = build_meta_block(edition, latest_id, og_url)
    replacement = f"<!-- BUILD:META:START -->\n{meta}\n<!-- BUILD:META:END -->"
    if not META_PATTERN.search(template_html):
        raise SystemExit("템플릿에 <!-- BUILD:META:START --> / <!-- BUILD:META:END --> 마커가 없습니다.")
    return META_PATTERN.sub(replacement, template_html)


def main() -> int:
    if not INDEX_HTML.is_file():
        print(f"Template not found: {INDEX_HTML}", file=sys.stderr)
        return 1
    template_html = INDEX_HTML.read_text(encoding="utf-8")

    editions = load_editions()
    if not editions:
        print("No editions found in data/", file=sys.stderr)
        return 1
    latest_id = editions[0]["id"]

    DATE_DIR.mkdir(exist_ok=True)

    # 1) 일자별 페이지
    for ed in editions:
        eid = ed["id"]
        page_dir = DATE_DIR / eid
        page_dir.mkdir(parents=True, exist_ok=True)

        og_url = f"{SITE_URL}date/{eid}/"
        out_html = render_page(template_html, ed, latest_id, og_url)
        (page_dir / "index.html").write_text(out_html, encoding="utf-8")
        print(f"✓ wrote {(page_dir / 'index.html').relative_to(PROJECT_ROOT)}")

        og_path = page_dir / "og.png"
        if not og_path.is_file():
            print(f"⚠ {og_path.relative_to(PROJECT_ROOT)} 없음 — generate_message.py를 먼저 실행하세요", file=sys.stderr)

    # 2) 루트 index.html (= 최신 호와 동일, og:url만 루트)
    latest = editions[0]
    root_og_url = SITE_URL  # 루트 URL
    out_html = render_page(template_html, latest, latest_id, root_og_url)
    INDEX_HTML.write_text(out_html, encoding="utf-8")
    print(f"✓ wrote index.html (latest = {latest_id})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
