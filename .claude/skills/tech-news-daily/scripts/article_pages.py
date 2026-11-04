#!/usr/bin/env python3
"""
기사별 '알기 쉽게 읽기' 페이지 생성 (build_site.py가 호출).

입력:  data/<id>.json            (그날 호, newsItems)
       data/analysis/<id>.json   (기사별 분석. 없으면 그 날은 기사 페이지를 만들지 않음)
출력:  date/<id>/<NN>/index.html (NN = 01~10)

분석 JSON 스키마 (articles[i]):
  order        int   — newsItems.order 와 같은 번호
  basis        "original" | "clip"   — 원문을 읽고 썼는지 / 클리핑 요약 범위에서만 썼는지
  oneLine      str   — 한 줄 요약
  what         [str] — 무슨 일인가 (문단)
  background   [str] — 배경(왜 지금)
  why          [{area, text}] — 왜 중요한가 (산업·일·생활)
  glossary     [{term, desc}] — 어려운 말 풀이 2~4개
  think        [str] — 더 생각해 볼 점
  notes        [str] — 확인 메모(클리핑과 원문이 다른 점 등), 선택
  sourcesRead  [{name, url, publishedAt?, note?}] — 실제로 읽은 원문
최상위: id, generatedAt, generator, fxNote
"""
import json
from pathlib import Path


def esc(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load_analysis(data_dir: Path, eid: str) -> dict | None:
    f = data_dir / "analysis" / f"{eid}.json"
    if not f.is_file():
        return None
    a = json.loads(f.read_text(encoding="utf-8"))
    return {int(x["order"]): x for x in a.get("articles", [])} | {"_meta": a}


CSS = """
:root{--bg:#fff;--bg-tint:#f3f1ec;--ink:#0a0a14;--ink-soft:#2d2d3a;--ink-mute:#777783;--rule:#e6e6ea;--rule-soft:#f2f2f5;--kaist-blue:#1f4899;--kaist-blue-deep:#15326b}
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:var(--bg);color:var(--ink);font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.brand{border-bottom:1px solid var(--rule);padding:18px 0}
.brand a{display:flex;align-items:center;justify-content:center;gap:12px}
.brand img{height:48px;width:auto}
.brand span{font-size:18px;font-weight:700;letter-spacing:-.015em}
.mast{background:var(--kaist-blue);color:#fff;padding:16px 0}
.mast-inner{max-width:760px;margin:0 auto;padding:0 24px;display:flex;justify-content:space-between;align-items:center;gap:12px;font-size:14px;font-weight:600}
.mast-inner a{opacity:.92}.mast-inner a:hover{opacity:1;text-decoration:underline}
.mast-inner b{font-family:'Inter',sans-serif;font-weight:800;letter-spacing:-.01em}
main{max-width:760px;margin:0 auto;padding:36px 24px 24px}
.num-row{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:10px}
.num{font-family:'Inter',sans-serif;font-weight:800;font-size:40px;line-height:1;color:var(--kaist-blue);letter-spacing:-.03em}
.badge{font-size:12px;font-weight:700;padding:3px 8px;border-radius:3px;border:1px solid var(--rule);color:var(--ink-mute)}
.badge.ok{border-color:#cfe0d4;color:#2f6b43;background:#f1f8f3}
.badge.clip{border-color:#f0d9b5;color:#8a5a12;background:#fdf6ea}
h1{font-size:clamp(24px,4.6vw,32px);line-height:1.3;letter-spacing:-.02em;font-weight:800;margin-bottom:22px}
.oneline{background:var(--bg-tint);border-left:4px solid var(--kaist-blue);padding:16px 18px;font-size:18px;line-height:1.65;font-weight:600;color:var(--ink);margin-bottom:8px;border-radius:0 4px 4px 0}
section{margin-top:34px}
h2{font-size:13px;font-weight:800;letter-spacing:.08em;color:var(--kaist-blue);border-top:3px solid var(--ink);padding-top:12px;margin-bottom:14px}
section p{font-size:17px;line-height:1.8;color:var(--ink-soft);margin-bottom:12px}
.why{display:grid;gap:10px}
.why div{border:1px solid var(--rule);border-radius:4px;padding:14px 16px}
.why b{display:inline-block;font-size:13px;font-weight:800;color:#fff;background:var(--kaist-blue);border-radius:3px;padding:2px 8px;margin-bottom:6px}
.why p{margin:0;font-size:16px}
.gloss{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.gloss div{background:var(--rule-soft);border-radius:4px;padding:14px 16px}
.gloss dt{font-weight:800;font-size:16px;margin-bottom:4px}
.gloss dd{font-size:15px;line-height:1.65;color:var(--ink-soft)}
ul.think{list-style:none}
ul.think li{position:relative;padding:10px 0 10px 26px;border-bottom:1px solid var(--rule);color:var(--ink-soft);line-height:1.7}
ul.think li::before{content:"?";position:absolute;left:0;top:10px;font-family:'Inter',sans-serif;font-weight:800;color:var(--kaist-blue)}
.src{display:flex;flex-direction:column;gap:8px}
.src a{display:flex;justify-content:space-between;align-items:center;gap:12px;border:1px solid var(--kaist-blue);border-radius:4px;padding:12px 14px;color:var(--kaist-blue);font-weight:700;transition:all .15s}
.src a:hover{background:var(--kaist-blue);color:#fff}
.src small{display:block;font-weight:500;font-size:13px;opacity:.8;margin-top:2px}
.notes{margin-top:14px;font-size:14px;color:var(--ink-mute);line-height:1.7}
.notes li{margin-left:18px}
.fine{margin-top:18px;font-size:13px;color:var(--ink-mute)}
nav.pn{max-width:760px;margin:24px auto 0;padding:0 24px 56px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
nav.pn a{border:1px solid var(--rule);border-radius:4px;padding:14px 16px;transition:all .15s;min-height:84px}
nav.pn a:hover{border-color:var(--kaist-blue);background:var(--rule-soft)}
nav.pn small{display:block;font-size:12px;font-weight:700;color:var(--kaist-blue);margin-bottom:4px}
nav.pn span{font-size:15px;font-weight:600;line-height:1.4}
nav.pn .next{text-align:right}
nav.pn .back{grid-column:1/-1;text-align:center;background:var(--kaist-blue);color:#fff;border-color:var(--kaist-blue);min-height:0;font-weight:700}
nav.pn .back:hover{background:var(--kaist-blue-deep);color:#fff}
nav.pn .empty{visibility:hidden}
@media (max-width:640px){
  html,body{font-size:16px}
  .brand img{height:38px}.brand span{font-size:15px}
  main{padding:26px 18px 16px}
  .num{font-size:32px}
  .oneline{font-size:16.5px}
  section p{font-size:16px}
  .gloss{grid-template-columns:1fr}
  nav.pn{padding:0 18px 40px}
  nav.pn a{min-height:0}
  nav.pn .empty{display:none}
  nav.pn{grid-template-columns:1fr}
}
"""


def render_article(edition: dict, item: dict, an: dict, meta: dict, site_url: str, base_path: str) -> str:
    eid = edition["id"]
    dow = edition.get("dayOfWeek", "")
    date_str = eid.replace("-", ".")
    nn = f'{item["order"]:02d}'
    items = edition["newsItems"]
    total = len(items)
    idx = next(i for i, it in enumerate(items) if it["order"] == item["order"])
    prev_it = items[idx - 1] if idx > 0 else None
    next_it = items[idx + 1] if idx < total - 1 else None

    page_url = f"{site_url}date/{eid}/{nn}/"
    og_image = f"{site_url}date/{eid}/og.png"
    title = f'{item["title"]} — 데일리 테크 브리프 {date_str}'
    desc = an.get("oneLine") or item.get("summary", "")

    basis = an.get("basis", "clip")
    badge = ('<span class="badge ok">원문 확인 후 작성</span>' if basis == "original"
             else '<span class="badge clip">원문 요약 기준</span>')

    def paras(lst):
        return "".join(f"<p>{esc(p)}</p>" for p in lst or [])

    why = "".join(
        f'<div><b>{esc(w.get("area", ""))}</b><p>{esc(w.get("text", ""))}</p></div>'
        for w in an.get("why", [])
    )
    gloss = "".join(
        f'<div><dt>{esc(g["term"])}</dt><dd>{esc(g["desc"])}</dd></div>'
        for g in an.get("glossary", [])
    )
    think = "".join(f"<li>{esc(t)}</li>" for t in an.get("think", []))

    srcs = an.get("sourcesRead") or item.get("sources", [])
    src_html = "".join(
        f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">'
        f'<span>{esc(s["name"])} 원문 보기'
        f'<small>{esc(" · ".join(x for x in [s.get("publishedAt", "").replace("-", "."), s.get("note", "")] if x))}</small></span>'
        f"<span>↗</span></a>"
        for s in srcs
    )
    notes = an.get("notes") or []
    notes_html = ("<ul class=\"notes\">" + "".join(f"<li>{esc(n)}</li>" for n in notes) + "</ul>") if notes else ""
    basis_line = ("이 페이지는 아래 원문을 직접 읽고, 원문에 근거가 있는 사실만으로 썼습니다."
                  if basis == "original" else
                  "원문을 읽지 못해 클리핑 요약에 있는 내용 범위에서만 썼습니다(원문 요약 기준).")
    fine = " ".join(x for x in [basis_line, meta.get("fxNote", "")] if x)

    edition_url = f"{base_path}date/{eid}/"

    def pn(it, cls, label):
        if not it:
            return f'<a class="{cls} empty" aria-hidden="true"></a>'
        return (f'<a class="{cls}" href="{base_path}date/{eid}/{it["order"]:02d}/">'
                f'<small>{label} · {it["order"]:02d}</small><span>{esc(it["title"])}</span></a>')

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(page_url)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(item["title"])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(og_image)}">
<meta property="og:url" content="{esc(page_url)}">
<meta property="og:site_name" content="KAIST 경영대학 테크 네트워크 · 데일리 테크 브리프">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(item["title"])}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(og_image)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css">
<style>{CSS}</style>
</head>
<body>
<header class="brand"><a href="{base_path}"><img src="{base_path}KCB_Logo.png" alt="KAIST College of Business"><span>KAIST 경영대학 테크 네트워크</span></a></header>
<div class="mast"><div class="mast-inner">
  <a href="{edition_url}">← 데일리 테크 브리프 {date_str} {esc(dow)}요일</a>
  <b>{nn} / {total:02d}</b>
</div></div>
<main>
  <div class="num-row"><div class="num">{nn}</div>{badge}</div>
  <h1>{esc(item["title"])}</h1>
  <p class="oneline">{esc(an.get("oneLine", ""))}</p>

  <section><h2>무슨 일인가</h2>{paras(an.get("what"))}</section>
  <section><h2>배경 — 왜 지금</h2>{paras(an.get("background"))}</section>
  <section><h2>왜 중요한가</h2><div class="why">{why}</div></section>
  <section><h2>어려운 말 풀이</h2><dl class="gloss">{gloss}</dl></section>
  <section><h2>더 생각해 볼 점</h2><ul class="think">{think}</ul></section>
  <section><h2>원문 · 출처</h2><div class="src">{src_html}</div>{notes_html}<p class="fine">{esc(fine)}</p></section>
</main>
<nav class="pn">
  {pn(prev_it, "prev", "← 이전 기사")}
  {pn(next_it, "next", "다음 기사 →")}
  <a class="back" href="{edition_url}#news-{item["order"]}">{date_str} 호 전체 보기</a>
</nav>
</body>
</html>
"""


def build_articles(edition: dict, data_dir: Path, date_dir: Path, site_url: str, base_path: str) -> list[int]:
    """그 호의 분석이 있으면 기사 페이지를 만들고, 만든 기사 번호 목록을 돌려준다."""
    analysis = load_analysis(data_dir, edition["id"])
    if not analysis:
        return []
    meta = analysis.pop("_meta")
    made = []
    for item in edition.get("newsItems", []):
        an = analysis.get(int(item["order"]))
        if not an:
            continue
        out_dir = date_dir / edition["id"] / f'{item["order"]:02d}'
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            render_article(edition, item, an, meta, site_url, base_path), encoding="utf-8"
        )
        made.append(int(item["order"]))
    return made
