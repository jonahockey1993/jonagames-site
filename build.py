#!/usr/bin/env python3
"""Bouwt de site jonagames.nl uit de bronnen in bron/.

    python build.py

Bronnen (de enige plek om iets aan te passen):
- bron/games.json                       welke games er zijn, met korte en lange tekst (NL + EN)
- bron/algemeen.nl.md, algemeen.en.md   de privacy-afspraken die voor alle games gelden
- bron/<slug>/privacy.nl.md, .en.md     de volledige privacyverklaring per game

Uitvoer (wordt gecommit, GitHub Pages serveert hem zo):
- index.html                            home met alle games
- privacy.html                          algemene privacy plus een link per game
- games/<slug>/index.html               pagina per game
- games/<slug>/privacy.html             privacyverklaring per game (deze URL gaat naar Play Console)
- app-ads.txt                           geen uitvoer van dit script: met de hand, AdMob-uitgevers-ID

Een nieuwe game: een blok in games.json en een map bron/<slug>/ met twee privacyteksten.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRON = ROOT / "bron"
MERK = "JonaGames"
CONTACT = "info@gereed3d.nl"


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"([\w.+-]+@[\w-]+\.[\w.]+[a-z])", r'<a href="mailto:\1">\1</a>', text)
    return re.sub(r"(https?://[^\s<)]+[^\s<).,])", r'<a href="\1">\1</a>', text)


def markdown(tekst: str) -> str:
    """Eenvoudige Markdown: koppen, alinea's, lijsten, vet, cursief, links."""
    out, in_list = [], False
    for raw in tekst.splitlines():
        line = raw.rstrip()
        if line.startswith(">"):
            continue  # conceptnotities horen niet op de openbare pagina
        if in_list and not line.startswith("- "):
            out.append("</ul>")
            in_list = False
        if not line:
            continue
        if line.startswith("## "):
            out.append(f"<h3>{inline(line[3:])}</h3>")
        elif line.startswith("# "):
            out.append(f"<h2>{inline(line[2:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


STYLE = """
:root { color-scheme: light; --tekst: #24443b; --accent: #2f5d50; --zacht: #4e8c7f; --vlak: #f7fbf9; }
* { box-sizing: border-box; }
body { margin: 0; font: 17px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: var(--tekst);
       background: linear-gradient(#e8f3ee, #cfe6df) fixed; }
.balk { position: sticky; top: 0; z-index: 10; background: rgba(247, 251, 249, .95);
        box-shadow: 0 1px 8px rgba(36, 68, 59, .1); }
.balk-in { max-width: 860px; margin: 0 auto; padding: 10px 16px; display: flex; align-items: center;
           gap: 18px; flex-wrap: wrap; }
.merk { font-weight: 600; letter-spacing: .06em; color: var(--accent); text-decoration: none; font-size: 1.15rem;
        margin-right: auto; }
.balk a, .balk summary { color: var(--accent); text-decoration: none; cursor: pointer; }
.balk a:hover, .balk summary:hover { text-decoration: underline; }
details.menu { position: relative; }
details.menu summary { list-style: none; }
details.menu summary::-webkit-details-marker { display: none; }
details.menu summary::after { content: " ▾"; font-size: .8em; }
details.menu[open] .lijst { display: block; }
.lijst { display: none; position: absolute; right: 0; top: 2em; min-width: 220px; background: #fff;
         border-radius: 14px; padding: 8px; box-shadow: 0 6px 24px rgba(36, 68, 59, .18); }
.lijst a { display: block; padding: 8px 12px; border-radius: 10px; }
.lijst a:hover { background: #e8f3ee; text-decoration: none; }
.lijst small { display: block; color: var(--zacht); font-size: .8rem; }
main { max-width: 760px; margin: 0 auto; padding: 24px 16px 64px; }
header.kop { text-align: center; padding: 24px 0 4px; }
header.kop h1 { font-weight: 300; letter-spacing: .06em; font-size: 2.1rem; margin: 0; color: var(--accent); }
header.kop p { margin: 4px 0 0; color: var(--zacht); }
nav.taal { text-align: center; margin: 12px 0 8px; }
nav.taal a { margin: 0 10px; color: var(--accent); }
section { background: var(--vlak); border-radius: 24px; padding: 8px 28px 24px; margin: 24px 0;
          box-shadow: 0 2px 10px rgba(36, 68, 59, .08); }
.kaarten { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.kaart { background: #fff; border-radius: 18px; padding: 16px 20px; text-decoration: none; color: var(--tekst);
         box-shadow: 0 2px 8px rgba(36, 68, 59, .08); }
.kaart:hover { box-shadow: 0 4px 16px rgba(36, 68, 59, .18); }
.kaart h3 { margin: 0 0 4px; }
.kaart .status { color: var(--zacht); font-size: .85rem; }
h2 { font-size: 1.4rem; margin-top: 1.2em; }
h3 { font-size: 1.08rem; margin: 1.4em 0 .3em; color: var(--accent); }
a { color: var(--accent); }
li { margin: .3em 0; }
footer { text-align: center; color: var(--zacht); font-size: .9rem; margin-top: 32px; }
"""

PAGINA = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<meta name="description" content="{omschrijving}">
<style>{style}</style>
</head>
<body>
<div class="balk"><div class="balk-in">
<a class="merk" href="/">{merk}</a>
<details class="menu"><summary>Games</summary><div class="lijst">
{gamemenu}
</div></details>
<a href="/privacy.html">Privacy</a>
<a href="/#contact">Contact</a>
</div></div>
<main>
{body}
<footer>{merk} · <a href="mailto:{contact}">{contact}</a></footer>
</main>
</body>
</html>
"""


def pagina(titel: str, omschrijving: str, body: str, games: list) -> str:
    menu = "\n".join(
        f'<a href="/games/{g["slug"]}/">{html.escape(g["naam"])}<small>{html.escape(g["kort"]["nl"])}</small></a>'
        for g in games
    )
    return PAGINA.format(
        titel=html.escape(titel),
        omschrijving=html.escape(omschrijving),
        style=STYLE,
        merk=MERK,
        gamemenu=menu,
        body=body,
        contact=CONTACT,
    )


def schrijf(pad: Path, inhoud: str) -> None:
    pad.parent.mkdir(parents=True, exist_ok=True)
    pad.write_text(inhoud, encoding="utf-8", newline="\n")
    print("geschreven:", pad.relative_to(ROOT))


def kaarten(games: list, taal: str) -> str:
    return '<div class="kaarten">\n' + "\n".join(
        f'<a class="kaart" href="/games/{g["slug"]}/"><h3>{html.escape(g["naam"])}</h3>'
        f'<p>{html.escape(g["kort"][taal])}</p><span class="status">{html.escape(g["status"][taal])}</span></a>'
        for g in games
    ) + "\n</div>"


def main() -> None:
    games = json.loads((BRON / "games.json").read_text(encoding="utf-8"))

    # Home
    home = f"""<header class="kop"><h1>{MERK}</h1><p>Games voor Android · Games for Android</p></header>
<section lang="nl">
<h2>Onze games</h2>
<p>Rustige, eerlijke games voor je telefoon. Geen account, geen opdringerige advertenties: een advertentie zie je alleen als je daar zelf voor kiest.</p>
{kaarten(games, "nl")}
</section>
<section lang="en">
<h2>Our games</h2>
<p>Calm, honest games for your phone. No account, no pushy adverts: you only see an advert if you choose to.</p>
{kaarten(games, "en")}
</section>
<section id="contact">
<h3>Contact</h3>
<p>{MERK} · <a href="mailto:{CONTACT}">{CONTACT}</a></p>
<p><a href="/privacy.html">Privacy</a></p>
</section>"""
    schrijf(ROOT / "index.html", pagina(MERK, "Games voor Android van JonaGames.", home, games))

    # Algemene privacy, met per game een link
    def lijst(taal: str) -> str:
        label = "Privacyverklaring" if taal == "nl" else "Privacy policy"
        items = "\n".join(
            f'<li><a href="/games/{g["slug"]}/privacy.html#{taal}">{html.escape(g["naam"])}</a> · {label}</li>'
            for g in games
        )
        kop = "Per game" if taal == "nl" else "Per game"
        return f"<h3>{kop}</h3>\n<ul>\n{items}\n</ul>"

    nl = markdown((BRON / "algemeen.nl.md").read_text(encoding="utf-8"))
    en = markdown((BRON / "algemeen.en.md").read_text(encoding="utf-8"))
    body = (
        '<nav class="taal"><a href="#nl">Nederlands</a> · <a href="#en">English</a></nav>\n'
        f'<section id="nl" lang="nl">\n{nl}\n{lijst("nl")}\n</section>\n'
        f'<section id="en" lang="en">\n{en}\n{lijst("en")}\n</section>'
    )
    schrijf(ROOT / "privacy.html", pagina(f"Privacy · {MERK}", "Privacy bij de games van JonaGames.", body, games))

    # Per game
    for g in games:
        slug, naam = g["slug"], g["naam"]
        uitgever = g["uitgever"]
        info = f"""<header class="kop"><h1>{html.escape(naam)}</h1><p>{html.escape(g["status"]["nl"])} · {html.escape(g["status"]["en"])}</p></header>
<section lang="nl">
<h2>{html.escape(g["kort"]["nl"])}</h2>
<p>{html.escape(g["lang"]["nl"])}</p>
<p>Uitgever: {html.escape(uitgever)} · <a href="privacy.html#nl">Privacyverklaring</a></p>
</section>
<section lang="en">
<h2>{html.escape(g["kort"]["en"])}</h2>
<p>{html.escape(g["lang"]["en"])}</p>
<p>Publisher: {html.escape(uitgever)} · <a href="privacy.html#en">Privacy policy</a></p>
</section>"""
        schrijf(ROOT / "games" / slug / "index.html", pagina(naam, g["kort"]["en"], info, games))

        pnl = markdown((BRON / slug / "privacy.nl.md").read_text(encoding="utf-8"))
        pen = markdown((BRON / slug / "privacy.en.md").read_text(encoding="utf-8"))
        body = (
            f'<header class="kop"><h1>{html.escape(naam)}</h1></header>\n'
            '<nav class="taal"><a href="#nl">Nederlands</a> · <a href="#en">English</a> · '
            f'<a href="/games/{slug}/">{html.escape(naam)}</a></nav>\n'
            f'<section id="nl" lang="nl">\n{pnl}\n</section>\n<section id="en" lang="en">\n{pen}\n</section>'
        )
        schrijf(ROOT / "games" / slug / "privacy.html", pagina(f"Privacy · {naam}", f"Privacy policy of {naam}.", body, games))


if __name__ == "__main__":
    main()
