"""WOO0103 개발자 페이지(dhwoo0103.github.io) 생성기.

각 앱 저장소의 docs/privacy-policy.md 를 HTML 로 바꾸고, 소개 페이지와 app-ads.txt 를 만든다.
방침을 고친 뒤에는 이 스크립트를 다시 돌리고 커밋·푸시하면 된다.

    python build.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS_DIR = ROOT.parent

# AdMob 계정(six05521, pub-2061...) 하나로 모든 앱의 광고를 판다. 빈 계정 pub-8323 은 넣지 않는다.
APP_ADS_TXT = "google.com, pub-2061854574621894, DIRECT, f08c47fec0942fa0\n"
CONTACT = "dh.woo0103@gmail.com"
YOUTUBE = "https://www.youtube.com/@얼마모을까"

APPS = [
    ("carcost", "자동차 유지비 계산기", "자동차세·취득세·월 유지비 계산, 경고등 사전, 소모품 교체 알림", "생활"),
    ("moabom", "얼마모을까", "적금·예금 세후 이자 계산, 목표 역산, 저축 계획과 저금통 키우기", "생활"),
    ("parkout", "이중주차 탈출", "차를 빼고 이중주차 차를 밀어 길을 여는 주차장 퍼즐", "게임"),
    ("moneysense", "돈감각 퀴즈", "하루 5문제로 키우는 이자 감각, 해설이 있는 돈 퀴즈", "게임"),
    ("stickshift", "클러치 마스터", "클러치·기어·언덕 출발을 연습하는 수동변속 시뮬레이터", "게임"),
    ("richrookie", "적금하면 또 부자됨", "첫 월급부터 1년 버티기, 세후 이자로 굴러가는 사회초년생 텍스트 키우기", "게임"),
    ("strangechat", "답장하면 안 되는 대화", "평범한 메신저 대화 속 위화감을 찾아 BAD END를 피하는 텍스트 호러", "게임"),
    ("factory", "반장 하면 또 공장장", "계약직 생산직에서 1년 안에 반장까지, 안전과 공수의 현장 키우기", "게임"),
    ("usedcar", "중고차 하면 또 사장님", "숨은 흠을 감별하고 정직하게 팔아 사장님이 되는 중고차 딜러 키우기", "게임"),
]

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--text:#1d2330;--muted:#5d6675;--line:#e3e6eb;--accent:#1e5eff;--chip:#eef2ff}
@media (prefers-color-scheme:dark){:root{--bg:#12151b;--card:#1b2029;--text:#e8ebf0;--muted:#9aa3b2;--line:#2b3240;--accent:#7aa2ff;--chip:#232b3d}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;word-break:keep-all}
main{max-width:760px;margin:0 auto;padding:28px 16px 56px}
a{color:var(--accent)}
h1{font-size:1.6rem;line-height:1.35;margin:.2em 0 .4em}
h2{font-size:1.12rem;margin:1.8em 0 .5em;padding-top:.6em;border-top:1px solid var(--line)}
.muted{color:var(--muted);font-size:.93rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}
.card h3{margin:0 0 4px;font-size:1.08rem}
.chip{display:inline-block;font-size:.78rem;padding:1px 9px;border-radius:99px;background:var(--chip);color:var(--accent);margin-left:6px;vertical-align:2px}
ul{padding-left:1.2em}
footer{margin-top:40px;color:var(--muted);font-size:.88rem}
nav{font-size:.92rem;margin-bottom:10px}
"""


def page(title: str, body: str, *, description: str) -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<style>{CSS}</style>
</head>
<body>
<main>
{body}
<footer>© 2026 WOO0103 · 문의 <a href="mailto:{CONTACT}">{CONTACT}</a></footer>
</main>
</body>
</html>
"""


LINK = re.compile(r"(https?://[^\s)]+)|([\w.+-]+@[\w-]+\.[\w.]+)")


def inline(text: str) -> str:
    out, pos = [], 0
    for m in LINK.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1):
            url = m.group(1)
            out.append(f'<a href="{html.escape(url)}">{html.escape(url)}</a>')
        else:
            mail = m.group(2)
            out.append(f'<a href="mailto:{html.escape(mail)}">{html.escape(mail)}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def md_to_html(md: str) -> tuple[str, str]:
    """이 저장소의 방침 문서에 쓰는 만큼만 지원한다: #, ##, - 목록, 문단."""
    lines = md.splitlines()
    title, parts, para, items = "", [], [], []

    def flush():
        nonlocal para, items
        if para:
            # 방침 문서는 문단을 한 줄로 쓰고, 머리글(수정일·적용 앱·개발자)만 줄을 나눠 쓴다.
            parts.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")
            para = []
        if items:
            parts.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
            items = []

    for raw in lines:
        line = raw.strip()
        if not line:
            flush()
        elif line.startswith("# "):
            flush()
            title = line[2:].strip()
            parts.append(f"<h1>{html.escape(title)}</h1>")
        elif line.startswith("## "):
            flush()
            parts.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("- "):
            if para:
                flush()
            items.append(line[2:].strip())
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return title, "\n".join(parts)


def build() -> None:
    (ROOT / "privacy").mkdir(exist_ok=True)
    (ROOT / "app-ads.txt").write_text(APP_ADS_TXT, encoding="utf-8", newline="\n")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

    cards = []
    for slug, name, desc, kind in APPS:
        md = (APPS_DIR / slug / "docs" / "privacy-policy.md").read_text(encoding="utf-8")
        title, body = md_to_html(md)
        nav = '<nav><a href="../">← WOO0103 앱 목록</a></nav>'
        (ROOT / "privacy" / f"{slug}.html").write_text(
            page(title, nav + body, description=f"{name} 개인정보 처리방침"),
            encoding="utf-8", newline="\n")
        cards.append(
            f'<div class="card"><h3>{html.escape(name)}<span class="chip">{kind}</span></h3>'
            f'<div class="muted">{html.escape(desc)}</div>'
            f'<div style="margin-top:8px"><a href="privacy/{slug}.html">개인정보 처리방침</a>'
            f' · Android · 출시 준비 중</div></div>')

    privacy_list = "".join(
        f'<li><a href="{slug}.html">{html.escape(name)}</a></li>' for slug, name, *_ in APPS)
    (ROOT / "privacy" / "index.html").write_text(
        page("개인정보 처리방침 | WOO0103",
             '<nav><a href="../">← WOO0103 앱 목록</a></nav><h1>개인정보 처리방침</h1>'
             f"<ul>{privacy_list}</ul>",
             description="WOO0103 앱별 개인정보 처리방침"),
        encoding="utf-8", newline="\n")

    index_body = (
        "<h1>WOO0103</h1>"
        '<p class="muted">생활에 바로 쓰는 계산기와 가볍게 즐기는 게임을 만드는 1인 개발자입니다. '
        "모든 앱은 회원가입 없이 쓰고, 입력한 내용은 휴대폰 안에만 저장됩니다.</p>"
        + "".join(cards)
        + "<h2>문의</h2>"
        f'<p>이메일 <a href="mailto:{CONTACT}">{CONTACT}</a><br>'
        f'유튜브 <a href="{html.escape(YOUTUBE)}">@얼마모을까</a> — 매일 1분 돈 공부</p>'
    )
    (ROOT / "index.html").write_text(
        page("WOO0103 | 앱 개발자", index_body,
             description="WOO0103이 만든 Android 앱과 게임, 개인정보 처리방침"),
        encoding="utf-8", newline="\n")
    print("built:", ", ".join(s for s, *_ in APPS))


if __name__ == "__main__":
    build()
