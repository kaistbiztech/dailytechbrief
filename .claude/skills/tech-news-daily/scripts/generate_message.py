#!/usr/bin/env python3
"""
Daily Tech Brief - 카톡 공유 산출물 생성기

입력: data/YYYY-MM-DD.json
출력: Message/YYYY-MM-DD/card.png + Message/YYYY-MM-DD/text.txt

사용법:
    python3 .claude/skills/tech-news-daily/scripts/generate_message.py data/2026-05-26.json

의존성: playwright (이미 설치됨)
"""
import base64
import json
import sys
from pathlib import Path

SITE_URL = "https://kaistbiztech.github.io/dailytechbrief/"
PROJECT_ROOT = Path(__file__).resolve().parents[4]   # /Users/cheil/dev/technews
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "kakao-card.html"
OUTPUT_BASE = PROJECT_ROOT / "Message"
LOGO_PATH = PROJECT_ROOT / "KCB_Logo.png"


def build_og_html(edition: dict) -> str:
    """OG 메타가 박힌 일자별 진입 페이지. 클릭 시 메인 페이지로 즉시 redirect.

    공유 URL: SITE_URL + <id>/ → 이 HTML이 응답.
    메신저(카톡·슬랙·페북·트위터)는 이 HTML의 <meta> 만 읽고 미리보기에 사용.
    """
    eid = edition["id"]
    date_str = eid.replace("-", ".")
    dow = edition.get("dayOfWeek", "")
    titles = edition.get("newsItems", [])
    headlines_preview = " · ".join(
        f'{it["order"]:02d} {it["title"]}' for it in titles[:3]
    )

    og_image = f"{SITE_URL}Message/{eid}/card.png"
    og_url = f"{SITE_URL}{eid}/"
    redirect_url = f"{SITE_URL}#{eid}"

    title = f"데일리 테크 브리프 — {date_str} {dow}요일"

    # HTML escape
    def esc(s: str) -> str:
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(headlines_preview)}">
<meta property="og:image" content="{esc(og_image)}">
<meta property="og:image:width" content="1080">
<meta property="og:image:height" content="1920">
<meta property="og:url" content="{esc(og_url)}">
<meta property="og:site_name" content="KAIST 경영대학 테크 네트워크">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(headlines_preview)}">
<meta name="twitter:image" content="{esc(og_image)}">
<meta http-equiv="refresh" content="0; url={esc(redirect_url)}">
<script>location.replace({json.dumps(redirect_url)});</script>
<style>
  body {{ font-family: -apple-system, 'Pretendard', sans-serif; padding: 40px; color: #333; }}
  a {{ color: #1f4899; }}
</style>
</head>
<body>
<p>{esc(title)}로 이동 중입니다… <a href="{esc(redirect_url)}">바로 이동</a></p>
</body>
</html>
"""


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
    parts.append(f"전체 보기 👉 {SITE_URL}{eid}/")

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

    # 각 카드: 번호 + 제목 + 3문장 요약
    for item in edition["newsItems"]:
        parts.append(f"{item['order']:02d}. {item['title']}")
        parts.append(item["summary"])
        parts.append("")

    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append(f"전체 보기 👉 {SITE_URL}{eid}/")
    parts.append("© KAIST 경영대학 테크 네트워크")
    return "\n".join(parts)


def logo_as_data_url() -> str | None:
    """KCB 로고 PNG를 base64 data: URL로 인코딩."""
    if not LOGO_PATH.is_file():
        return None
    b = LOGO_PATH.read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


def generate_card_png(edition: dict, out_path: Path) -> None:
    """Playwright로 9:16 카드 PNG 생성."""
    from playwright.sync_api import sync_playwright

    template_url = TEMPLATE.resolve().as_uri()
    logo_url = logo_as_data_url()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=2)
        page = ctx.new_page()
        page.goto(template_url, wait_until="networkidle")
        page.evaluate(
            "([ed, logo]) => window.renderEdition(ed, logo)",
            [edition, logo_url],
        )
        # 폰트·이미지 적용 대기
        page.wait_for_timeout(700)
        page.screenshot(path=str(out_path), full_page=False, type="png")
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
    out_dir = OUTPUT_BASE / edition["id"]
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) 텍스트
    text_path = out_dir / "text.txt"
    text_path.write_text(build_text(edition), encoding="utf-8")
    print(f"✓ wrote {text_path.relative_to(PROJECT_ROOT)}")

    # 2) 이미지
    card_path = out_dir / "card.png"
    generate_card_png(edition, card_path)
    print(f"✓ wrote {card_path.relative_to(PROJECT_ROOT)}")

    # 3) 일자별 OG 진입 페이지 (프로젝트 루트의 {id}/index.html)
    share_dir = PROJECT_ROOT / edition["id"]
    share_dir.mkdir(parents=True, exist_ok=True)
    og_path = share_dir / "index.html"
    og_path.write_text(build_og_html(edition), encoding="utf-8")
    print(f"✓ wrote {og_path.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
