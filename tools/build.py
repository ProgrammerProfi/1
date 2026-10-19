"""Собирает статический сайт с разборами задач ЕГЭ.

python3 tools/build.py            — собрать сайт в корень репозитория
Количество задач растёт на 1 в день на каждый номер (от START_DATE),
так что ежедневный запуск добавляет новые страницы без участия человека.
"""
import datetime as dt
import hashlib
import html
import json
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gen import GENERATORS  # noqa: E402
from theory import THEORY  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("SITE_BASE", "https://programmerprofi.github.io/1/")
BOT = "https://t.me/informtrainbot"
START_DATE = dt.date(2026, 10, 19)
BASE_COUNT = 40
PER_DAY = 1
INDEXNOW_KEY = "3f9c2a7e5b1d4c8fa06e92b7d4c1e835"
CACHE = os.path.join(ROOT, "tools", "verified.json")


def today():
    s = os.environ.get("BUILD_DATE")
    return dt.date.fromisoformat(s) if s else dt.date.today()


def run_code(code):
    try:
        r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def norm(s):
    return "\n".join(" ".join(line.split()) for line in s.strip().splitlines())


def collect(num, need, cache):
    gen = GENERATORS[num][0]
    tasks, seen = [], set()
    seed = 0
    while len(tasks) < need and seed < need * 20:
        rng = random.Random(num * 1_000_003 + seed)
        seed += 1
        t = gen(rng)
        if not t:
            continue
        key = hashlib.sha1(t["statement"].encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        ck = hashlib.sha1((t["code"] + "\0" + t["answer"]).encode()).hexdigest()
        if ck not in cache:
            out = run_code(t["code"])
            cache[ck] = out is not None and norm(out) == norm(t["answer"])
        if not cache[ck]:
            print(f"  [skip] №{num} seed {seed - 1}: код и ответ генератора разошлись", file=sys.stderr)
            continue
        t["num"] = num
        t["idx"] = len(tasks) + 1
        added = max(0, t["idx"] - BASE_COUNT)
        t["date"] = (START_DATE + dt.timedelta(days=(added + PER_DAY - 1) // PER_DAY)).isoformat()
        tasks.append(t)
    return tasks


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1c1a;--muted:#6b675f;--line:#e4e0d8;--card:#ffffff;--accent:#2f5bd3;--accent-fg:#fff;--code:#f3f1ec;--ok:#1f7a45;--bad:#b3261e}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141413;--fg:#ecebe7;--muted:#a19d94;--line:#2c2b28;--card:#1c1c1a;--accent:#7a9bff;--accent-fg:#0d0d0c;--code:#22221f;--ok:#5fcf8c;--bad:#ff8a80}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:var(--accent)}
.wrap{max-width:760px;margin:0 auto;padding:0 16px}
header{border-bottom:1px solid var(--line)}
header .wrap{display:flex;gap:16px;align-items:center;justify-content:space-between;padding-top:14px;padding-bottom:14px}
.logo{font-weight:700;text-decoration:none;color:var(--fg)}
.navbot{font-size:15px}
h1{font-size:28px;line-height:1.25;margin:28px 0 8px}
h2{font-size:21px;margin:32px 0 10px}
.sub{color:var(--muted);margin:0 0 20px}
.crumbs{font-size:14px;color:var(--muted);margin-top:18px}.crumbs a{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0}
pre,code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:14.5px}
code{background:var(--code);padding:1px 5px;border-radius:5px}
pre{position:relative;background:var(--code);padding:14px 16px;border-radius:10px;overflow-x:auto;line-height:1.5;margin:12px 0}
pre code{background:none;padding:0;display:block}pre:has(.copy) code{padding-top:22px}
.formula{font-family:Georgia,"Times New Roman",serif;font-size:18px;padding:6px 0 6px 14px;border-left:3px solid var(--line)}
.cta{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:12px;padding:16px 20px;margin:28px 0}
.cta p{margin:0;flex:1 1 300px}
.btn{display:inline-block;background:var(--accent);color:var(--accent-fg);text-decoration:none;font-weight:600;padding:10px 18px;border-radius:9px;border:0;font-size:16px;cursor:pointer}
.check{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-start}
.check input,.check textarea{flex:1 1 220px;font:inherit;padding:9px 12px;border-radius:9px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}
.res{margin-top:10px;font-weight:600}.res.ok{color:var(--ok)}.res.bad{color:var(--bad)}
details summary{cursor:pointer;font-weight:600}
ol.steps li{margin:8px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:16px 0}
.grid a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--fg)}
.grid a b{display:block;font-size:19px;color:var(--accent)}.grid a span{color:var(--muted);font-size:14px}
ul.tasks{list-style:none;padding:0;margin:0}ul.tasks li{border-bottom:1px solid var(--line);padding:9px 0}
ul.tasks small{color:var(--muted)}
.pager{display:flex;justify-content:space-between;gap:12px;margin:24px 0;font-size:15px}
footer{border-top:1px solid var(--line);margin-top:48px;color:var(--muted);font-size:14px}footer .wrap{padding-top:18px;padding-bottom:28px}
.copy{position:absolute;top:8px;right:8px;font-size:13px;background:none;border:1px solid var(--line);color:var(--muted);border-radius:6px;padding:2px 8px;cursor:pointer}
"""

JS = """
function chk(id){var i=document.getElementById('in'+id),r=document.getElementById('res'+id);
var n=function(s){return s.trim().split(/\\n+/).map(function(l){return l.trim().split(/\\s+/).join(' ')}).join('\\n')};
var a=decodeURIComponent(escape(atob(i.dataset.a)));
if(n(i.value)===n(a)){r.textContent='Верно!';r.className='res ok'}else{r.textContent='Пока нет. Проверь разбор ниже.';r.className='res bad'}}
function cp(b){var t=b.parentNode.querySelector('code').innerText;try{navigator.clipboard.writeText(t);b.textContent='Скопировано'}catch(e){}}
"""


def page(title, desc, path, body, ld=None):
    canon = BASE + path
    ldj = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article"><meta property="og:url" content="{canon}"><meta property="og:locale" content="ru_RU">
<style>{CSS}</style>{ldj}</head><body>
<header><div class="wrap"><a class="logo" href="{rel(path, '')}">ЕГЭ информатика: разборы</a><a class="navbot" href="{BOT}">Тренажёр в Telegram →</a></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Задачи сгенерированы по образцу заданий ЕГЭ, ответы проверены запуском кода. Тренировка с проверкой и статистикой — в боте <a href="{BOT}">@informtrainbot</a>.</div></footer>
<script>{JS}</script></body></html>"""


def rel(frm, to):
    depth = frm.count("/")
    return "../" * depth + to if to else ("../" * depth or "./")


def cta(text):
    return (f'<div class="cta"><p>{text}</p><a class="btn" href="{BOT}">Открыть бота</a></div>')


def strip_tags(s):
    out, skip = [], False
    for ch in s:
        if ch == "<":
            skip = True
        elif ch == ">":
            skip = False
        elif not skip:
            out.append(ch)
    return html.unescape("".join(out))


def task_page(t, prev, nxt, total):
    num, idx = t["num"], t["idx"]
    path = f"zadanie-{num}/{idx}.html"
    topic = GENERATORS[num][1]
    title = f"Задание {num} ЕГЭ по информатике №{idx}: {t['title']} — разбор и решение на Python"
    desc = strip_tags(t["statement"])[:155].rsplit(" ", 1)[0] + "…"
    b64 = __import__("base64").b64encode(t["answer"].encode()).decode()
    multi = "\n" in t["answer"]
    inp = (f'<textarea id="in{idx}" rows="4" data-a="{b64}" placeholder="Числа через пробел, каждая пара с новой строки"></textarea>' if multi
           else f'<input id="in{idx}" data-a="{b64}" placeholder="Твой ответ" autocomplete="off">')
    steps = "".join(f"<li>{s}</li>" for s in t["steps"])
    nav = '<div class="pager">' + (f'<a href="{prev}.html">← Задача {prev}</a>' if prev else "<span></span>") + \
          f'<a href="./">Все задачи №{num}</a>' + (f'<a href="{nxt}.html">Задача {nxt} →</a>' if nxt else "<span></span>") + "</div>"
    body = f"""<div class="crumbs"><a href="../">Главная</a> / <a href="./">Задание {num}</a> / задача {idx}</div>
<h1>Задание {num} ЕГЭ по информатике: задача {idx}</h1>
<p class="sub">{topic} · добавлено {t['date']}</p>
<div class="card">{t['statement']}</div>
<h2>Проверь себя</h2>
<div class="check">{inp}<button class="btn" onclick="chk({idx})">Проверить</button></div><div id="res{idx}" class="res"></div>
{cta(f"Хочешь такие задачи каждый день? Тренажёр в Telegram даёт задачи №{num} и других номеров, сразу проверяет ответ и показывает, где ты проседаешь.")}
<h2>Разбор</h2>
<details><summary>Показать решение</summary>
<ol class="steps">{steps}</ol>
<h2>Код решения на Python</h2>
<pre><button class="copy" onclick="cp(this)">Копировать</button><code>{html.escape(t['code'])}</code></pre>
<p>Программа печатает ответ, её можно вставить в любую IDE на экзамене как есть.</p>
</details>
{nav}"""
    ld = {"@context": "https://schema.org", "@type": "Quiz", "name": title, "about": f"Задание {num} ЕГЭ по информатике",
          "educationalLevel": "11 класс", "inLanguage": "ru", "datePublished": t["date"],
          "hasPart": [{"@type": "Question", "name": strip_tags(t["statement"])[:300],
                       "acceptedAnswer": {"@type": "Answer", "text": t["answer"]}}]}
    return path, page(title, desc, path, body, ld)


def hub_page(num, tasks):
    path = f"zadanie-{num}/index.html"
    topic = GENERATORS[num][1]
    th = THEORY.get(num, "")
    title = f"Задание {num} ЕГЭ по информатике: {topic.lower()} — теория, разборы и {len(tasks)} задач с ответами"
    desc = f"Как решать задание {num} ЕГЭ по информатике: идея, шаблон кода на Python, типичные ошибки и {len(tasks)} задач с разборами и проверкой ответа."
    items = "".join(f'<li><a href="{t["idx"]}.html">Задача {t["idx"]}</a> <small>— {html.escape(t["title"])}</small></li>'
                    for t in reversed(tasks))
    body = f"""<div class="crumbs"><a href="../">Главная</a> / задание {num}</div>
<h1>Задание {num} ЕГЭ по информатике</h1><p class="sub">{topic}</p>
{th}
{cta(f"Задачи №{num} с мгновенной проверкой, статистикой и пробниками — в Telegram-тренажёре.")}
<h2>Задачи с разбором ({len(tasks)})</h2><p class="sub">Новые задачи добавляются каждый день.</p>
<ul class="tasks">{items}</ul>"""
    return path, page(title, desc, path, body)


def index_page(all_tasks):
    cards = "".join(f'<a href="zadanie-{n}/"><b>№{n}</b><span>{GENERATORS[n][1]} · {len(all_tasks[n])} задач</span></a>' for n in sorted(all_tasks))
    latest = sorted((t for ts in all_tasks.values() for t in ts), key=lambda t: (t["date"], t["num"], t["idx"]), reverse=True)[:15]
    lst = "".join(f'<li><a href="zadanie-{t["num"]}/{t["idx"]}.html">№{t["num"]}, задача {t["idx"]}</a> <small>— {html.escape(t["title"])}</small></li>' for t in latest)
    total = sum(len(v) for v in all_tasks.values())
    body = f"""<h1>Разборы заданий ЕГЭ по информатике с решениями на Python</h1>
<p class="sub">{total} задач по {len(all_tasks)} номерам. У каждой — пошаговый разбор, готовый код и проверка ответа. Каждый день добавляются новые.</p>
{cta("Решаешь ЕГЭ по информатике? В Telegram-тренажёре больше 6000 задач по 25 номерам, проверка ответа, статистика по слабым местам и пробники.")}
<h2>Номера</h2><div class="grid">{cards}</div>
<h2>Новые задачи</h2><ul class="tasks">{lst}</ul>
<h2>Как устроен сайт</h2>
<p>Каждая задача сгенерирована программой по образцу реального задания ЕГЭ. Ответ считается двумя независимыми способами: генератором и кодом из разбора. Если они не совпали, задача на сайт не попадает.</p>"""
    title = "ЕГЭ по информатике: разборы заданий с решениями на Python"
    desc = f"{total} задач ЕГЭ по информатике с пошаговыми разборами, кодом на Python и проверкой ответа. Задания 5, 7, 8, 11–16, 23, 25."
    return "index.html", page(title, desc, "index.html", body,
                              {"@context": "https://schema.org", "@type": "WebSite", "name": title, "url": BASE, "inLanguage": "ru"})


def main():
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    days = (today() - START_DATE).days
    need = BASE_COUNT + max(0, days) * PER_DAY
    all_tasks = {}
    for num in GENERATORS:
        all_tasks[num] = collect(num, need, cache)
        print(f"№{num}: {len(all_tasks[num])} задач", file=sys.stderr)
    json.dump(cache, open(CACHE, "w"), indent=0, sort_keys=True)

    files = {}
    for num, ts in all_tasks.items():
        p, h = hub_page(num, ts)
        files[p] = (h, max(t["date"] for t in ts))
        for i, t in enumerate(ts):
            prev = ts[i - 1]["idx"] if i > 0 else None
            nxt = ts[i + 1]["idx"] if i + 1 < len(ts) else None
            p, h = task_page(t, prev, nxt, len(ts))
            files[p] = (h, t["date"])
    p, h = index_page(all_tasks)
    files[p] = (h, today().isoformat())

    for p, (h, _) in files.items():
        full = os.path.join(ROOT, p)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(h)

    urls = []
    for p, (_, d) in sorted(files.items()):
        loc = BASE + (p[:-len("index.html")] if p.endswith("index.html") else p)
        urls.append(f"<url><loc>{loc}</loc><lastmod>{d}</lastmod></url>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(ROOT, f"{INDEXNOW_KEY}.txt"), "w") as f:
        f.write(INDEXNOW_KEY)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    # список новых за сегодня — для IndexNow
    new = [BASE + p for p, (_, d) in files.items() if d == today().isoformat() and not p.endswith("index.html")]
    new += [BASE, *(BASE + f"zadanie-{n}/" for n in all_tasks)]
    with open(os.path.join(ROOT, "tools", "changed.txt"), "w") as f:
        f.write("\n".join(new) + "\n")
    print(f"страниц: {len(files)}", file=sys.stderr)


if __name__ == "__main__":
    main()
