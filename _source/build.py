"""Builds index.html for the Theoretical Cosmology and Gravity group page.

Shares its stylesheet with Ivonne's page (../izsite/template.html) so both look like one family.
"""
import base64, datetime as dt, html, re, sys, pathlib
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "izsite"))
import data
from build_helpers import chirp_path
import math, random


def background_path(w=560, h=46, n=420, seed=7):
    """A stochastic gravitational-wave background: many superposed waves with random phases."""
    rng = random.Random(seed)
    modes = [(rng.uniform(4, 40), rng.uniform(0, 2 * math.pi), rng.uniform(0.4, 1.0)) for _ in range(14)]
    ys = [sum(a * math.sin(2 * math.pi * f * k / n + p) for f, p, a in modes) for k in range(n + 1)]
    m = max(abs(y) for y in ys)
    return "M" + " L".join(f"{k / n * w:.1f},{h / 2 - y / m * (h / 2 - 3):.1f}" for k, y in enumerate(ys))

E = html.escape
TODAY = dt.date.today()


def fmt_date(iso, year=True):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%-d %b %Y") if year else d.strftime("%-d %b")


def academic_year(iso):
    d = dt.date.fromisoformat(iso)
    y = d.year if d.month >= 9 else d.year - 1
    return f"{y}/{str(y + 1)[2:]}"


def talk_li(t, show_year=False, tag_upcoming=True):
    date, who, aff, title, note, link = t
    title, link = "", ""  # programme lists speakers only
    future = dt.date.fromisoformat(date) >= TODAY
    tags = ""
    if note:
        tags += f'<span class="tag">{E(note)}</span>'
    if future and tag_upcoming:
        tags += '<span class="tag up">Upcoming</span>'
    aff_html = f' <span class="aff">· {E(aff)}</span>' if aff else ""
    title_html = (f'<span class="title">{E(title)}</span>' if title
                  else "")
    link_html = f'<a class="paper" href="{E(link)}">Related paper</a>' if link else ""
    return (f'<li class="talk" data-date="{date}"><span class="when">{fmt_date(date, show_year)}</span>'
            f'<span><span class="who">{E(who)}</span>{aff_html}{tags}{title_html}{link_html}</span></li>')


def build():
    css = (HERE.parent / "izsite" / "template.html").read_text()
    shared_css = re.search(r"<style>(.*?)</style>", css, re.S).group(1)

    talks = sorted(data.SEMINARS, key=lambda t: t[0])
    upcoming = [t for t in talks if dt.date.fromisoformat(t[0]) >= TODAY]
    up_html = "".join(talk_li(t, True, False) for t in upcoming) or '<li class="empty">The next programme will appear here soon.</li>'

    years = {}
    for t in talks:
        years.setdefault(academic_year(t[0]), []).append(t)
    year_html = []
    for i, (y, ts) in enumerate(sorted(years.items(), reverse=True)):
        items = "".join(talk_li(t) for t in sorted(ts, key=lambda t: t[0], reverse=True))
        year_html.append(
            f'<details class="year"{" open" if i == 0 else ""}><summary>{y} <span class="count">{len(ts)} talks</span></summary>'
            f'<ol class="talks">{items}</ol></details>')

    if upcoming:
        n = upcoming[0]
        title = ""
        aff = f" ({E(n[2])})" if n[2] else ""
        next_html = (f'<div class="next" id="next-talk" data-date="{n[0]}"><span class="label">Next group seminar</span>'
                     f'<span class="who">{E(n[1])}{aff}{title}</span>'
                     f'<span class="meta">{fmt_date(n[0])} · {E(data.SEMINAR_SLOT)}</span></div>')
    else:
        next_html = ""

    fac_html = []
    links = []
    for name, blurb, url in data.FACULTY:
        go = (f'<a class="go" href="{E(url)}">Personal page →</a>' if url
              else '<span class="soon-tag">Personal page coming soon</span>')
        fac_html.append(f'<article class="fac"><h3>{E(name)}</h3><p>{E(blurb)}</p>{go}</article>')
        links.append(f'<li><a href="{E(url)}">{E(name)}</a></li>' if url
                     else f'<li><span class="soon">{E(name)}</span> <span class="soon-tag">coming soon</span></li>')

    def group(title, rows):
        lis = "".join(f'<li><span class="name">{E(n)}</span>' + (f'<span class="note">{E(x)}</span>' if x else "") + "</li>"
                      for n, x in rows)
        return f'<div><h3 class="sub-h">{E(title)}</h3><ul>{lis}</ul></div>'
    people = "\n".join([
        group("PhD students", data.PHD_CURRENT),
        group("Former postdocs", data.POSTDOCS_FORMER),
        group("Former PhD students", data.PHD_FORMER),
        group("Visiting students", data.VISITING),
    ])

    page = (HERE / "template.html").read_text()
    for k, v in {
        "{{SHARED_CSS}}": shared_css, "{{CHIRP}}": background_path(), "{{NEXT_TALK}}": next_html,
        "{{FACULTY}}": "\n".join(fac_html), "{{FACULTY_LINKS}}": "\n".join(links), "{{PEOPLE}}": people,
        "{{SLOT}}": E(data.SEMINAR_SLOT), "{{UPCOMING}}": up_html, "{{YEARS}}": "\n".join(year_html),
    }.items():
        page = page.replace(k, v)

    img_dir = HERE.parent / "izsite" / "img"
    page = re.sub(r"\{\{IMG:([\w.-]+)\}\}",
                  lambda m: "data:image/jpeg;base64," + base64.b64encode((img_dir / m.group(1)).read_bytes()).decode(), page)
    assert "{{" not in page, re.findall(r"\{\{\w+\}\}", page)
    (HERE / "index.html").write_text(page)
    print("wrote", len(page), "bytes;", len(talks), "talks,", len(upcoming), "upcoming")


if __name__ == "__main__":
    build()
