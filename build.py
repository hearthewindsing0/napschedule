#!/usr/bin/env python3
"""Static site generator for napschedule.com. Output goes to docs/ (served by GitHub Pages).

Monetization settings: fill these in, run `python3 build.py`, commit, push.
"""
import json, os, shutil, html, datetime, hashlib
from content_ages import AGES
from content_guides import GUIDES
from content_babywise import BW_STAGES, BOOK

# ---- Monetization config -------------------------------------------------
AMAZON_TAG = ""        # Amazon Associates tracking ID, e.g. "napschedule-20"
ADSENSE_CLIENT = ""    # AdSense publisher ID, e.g. "ca-pub-1234567890123456"
# --------------------------------------------------------------------------

SITE = "https://napschedule.com"
NAME = "NapSchedule"
OUT = "docs"
TODAY = datetime.date.today().isoformat()

BOOKS = [
    ("On Becoming Babywise", "On Becoming Babywise Ezzo Bucknam",
     "The original book behind the eat-wake-sleep routine, covering birth to about 5 months: full feedings, the feed-wake-sleep cycle and how feeds merge over time."),
    ("On Becoming Babywise Book Two", "On Becoming Babywise Book Two Ezzo",
     "The follow-up for roughly 5 to 15 months: solids, naps, the move to fewer feeds and early toddler routines."),
    ("On Becoming Pretoddlerwise", "On Becoming Pretoddlerwise Ezzo",
     "The Ezzos' book for the 12 to 18 month stretch, including the transition to one nap."),
    ("On Becoming Toddlerwise", "On Becoming Toddlerwise Ezzo",
     "Routines, naps and structure for toddlers from about 18 months to 3 years."),
]

GEAR = [
    ("White noise machine", "white noise machine baby",
     "Steady white noise masks household sounds and can help babies link sleep cycles. Choose one with a continuous sound (not a timer that shuts off) and keep it at a moderate volume, across the room from the crib."),
    ("Blackout curtains or shades", "blackout curtains nursery",
     "A dark room is one of the easiest ways to lengthen daytime naps, especially in summer. Portable, suction-cup blackout shades are great for travel."),
    ("Wearable blanket (sleep sack)", "baby sleep sack wearable blanket",
     "Keeps your baby warm without loose blankets in the crib. Pick a TOG rating that matches your room temperature."),
    ("Transition swaddle", "transition swaddle arms free",
     "For babies who are starting to roll but still like a snug feel. Arms-free designs are the safe choice once rolling begins."),
    ("Toddler OK-to-wake clock", "ok to wake clock toddler",
     "A clock that changes color when it's time to get up. Very helpful for toddlers in a big-kid bed and for quiet time."),
    ("Room thermometer / hygrometer", "nursery room thermometer hygrometer",
     "Helps you dress your baby for the room. Most families aim for a comfortable room temperature, roughly 68–72°F (20–22°C)."),
]


def amazon_url(query):
    from urllib.parse import quote_plus
    url = "https://www.amazon.com/s?k=" + quote_plus(query)
    if AMAZON_TAG:
        url += "&tag=" + AMAZON_TAG
    return url


def esc(s):
    return html.escape(s, quote=True)


def fmt_time(minutes):
    minutes %= 24 * 60
    h, m = divmod(minutes, 60)
    ap = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {ap}"


def fmt_range(a, b):
    x, y = fmt_time(a), fmt_time(b)
    if x[-2:] == y[-2:]:
        return f"{x[:-3]}–{y}"
    return f"{x}–{y}"


def fmt_dur(m):
    h, mm = divmod(m, 60)
    if h and mm:
        return f"{h} hr {mm} min"
    if h:
        return f"{h} hr" if h == 1 else f"{h} hrs"
    return f"{mm} min"


def schedule_rows(age, wake=7 * 60):
    rows = [(fmt_time(wake), "Wake up, feed, start the day")]
    t = wake
    for i, nap in enumerate(age["naps"]):
        t += age["ww"][i]
        rows.append((fmt_range(t, t + nap), f"Nap {i + 1} ({fmt_dur(nap)})"))
        t += nap
    t += age["ww"][len(age["naps"])]
    rows.append((fmt_time(t), "Bedtime (start routine 20–30 minutes earlier)"))
    return rows


# ---------------------------------------------------------------------------
CSS = """
:root{--bg:#faf7f2;--bg2:#f3eee5;--card:#fff;--ink:#1f2433;--muted:#5b6275;--line:#e8e1d5;--brand:#2f4a75;--brand-ink:#fff;--accent:#e3a564;--accent-soft:#fbeedd;--accent-ink:#a5621f;--soft:#eef2f8;
--feed:#e3a564;--nap:#7a9cc6;--night:#4a4e8f;--wake:#9bbf8a;--shadow:0 1px 2px rgba(31,36,51,.04),0 4px 16px rgba(31,36,51,.06);--r:14px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12151f;--bg2:#181c29;--card:#1c2130;--ink:#e9e6f0;--muted:#a3a9bb;--line:#2b3144;--brand:#9db8e8;--brand-ink:#12151f;--accent:#e9b27a;--accent-soft:#2a2620;--accent-ink:#e9b27a;--soft:#20263a;--nap:#88a8d4;--night:#9a9de6;--shadow:0 1px 2px rgba(0,0,0,.3)}}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--brand);text-underline-offset:3px;text-decoration-thickness:1px}a:hover{text-decoration-thickness:2px}
.wrap{max-width:800px;margin:0 auto;padding:0 20px}
h1,h2,h3,.logo{font-family:Fraunces,Georgia,"Times New Roman",serif;font-optical-sizing:auto;letter-spacing:-.01em}
h1{font-size:2.3rem;line-height:1.15;margin:.3em 0 .35em;font-weight:650}
h2{font-size:1.5rem;line-height:1.25;margin:2em 0 .5em;font-weight:600}h3{font-size:1.15rem;margin:1.5em 0 .3em;font-weight:600}
.lead{font-size:1.12rem;color:var(--muted);margin-top:0}
header.site{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:saturate(1.4) blur(10px);-webkit-backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:60px}
.logo{display:flex;align-items:center;gap:8px;font-weight:700;font-size:1.25rem;text-decoration:none;color:var(--ink)}.logo .wm b{color:var(--accent);font-weight:700}
.logo svg{width:28px;height:28px;flex:none}
nav{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}nav::-webkit-scrollbar{display:none}
nav a{padding:6px 10px;border-radius:999px;text-decoration:none;font-weight:600;font-size:.93rem;white-space:nowrap;color:var(--ink)}
nav a:hover{background:var(--bg2)}
main{padding:22px 0 56px}
.hero{background:linear-gradient(160deg,var(--soft),var(--accent-soft));border:1px solid var(--line);border-radius:22px;padding:30px 26px;margin:6px 0 10px;position:relative;overflow:hidden}
.hero h1{margin-top:0}.hero .lead{max-width:34em}
.hero:after{content:"";position:absolute;right:-40px;top:-40px;width:160px;height:160px;border-radius:50%;box-shadow:-26px 26px 0 0 var(--accent);opacity:.25}
table{width:100%;border-collapse:separate;border-spacing:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;margin:1em 0;font-size:.97rem;box-shadow:var(--shadow)}
th,td{padding:11px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:var(--bg2);font-size:.82rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}tr:last-child td{border-bottom:0}
.glance td:first-child{font-weight:600;width:44%;color:var(--muted)}.glance td:last-child{font-weight:600}
.tl td:first-child{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:600;width:1%}
.tl td:last-child{position:relative;padding-left:34px}
.tl td:last-child:before{content:"";position:absolute;left:14px;top:18px;width:10px;height:10px;border-radius:50%;background:var(--wake)}
.tl tr.feed td:last-child:before{background:var(--feed)}.tl tr.nap td:last-child:before{background:var(--nap)}.tl tr.night td:last-child:before{background:var(--night)}
.tl tr.nap{background:color-mix(in srgb,var(--nap) 9%,transparent)}.tl tr.night{background:color-mix(in srgb,var(--night) 10%,transparent)}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:.85rem;color:var(--muted);margin:.4em 0 0}.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px 22px;margin:18px 0;box-shadow:var(--shadow)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;padding:0;margin:0;list-style:none}
.grid a{display:flex;flex-direction:column;align-items:flex-start;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:15px 18px;text-decoration:none;font-weight:650;color:var(--ink);box-shadow:var(--shadow);transition:transform .15s,border-color .15s}
.grid a:hover{transform:translateY(-2px);border-color:var(--accent)}
.grid.g4{grid-template-columns:repeat(4,1fr)}.grid.g5{grid-template-columns:repeat(5,1fr)}.grid.g5 a{padding:13px 14px}
.grid .t{white-space:nowrap}.grid .chip{white-space:nowrap}
@media(max-width:760px){.grid.g4,.grid.g5{grid-template-columns:1fr 1fr}.grid.g4>li:last-child:nth-child(odd),.grid.g5>li:last-child:nth-child(odd){grid-column:1/-1}}
.grid a small{display:block;font-weight:400;color:var(--muted);margin-top:2px}
.btn{display:inline-block;background:var(--brand);color:var(--brand-ink);padding:12px 22px;border-radius:999px;text-decoration:none;font-weight:700;border:0;cursor:pointer;font-size:1rem;box-shadow:0 2px 8px color-mix(in srgb,var(--brand) 35%,transparent)}
.btn:hover{filter:brightness(1.08);color:var(--brand-ink)}
.note{font-size:.88rem;color:var(--muted);background:var(--bg2);border-radius:10px;padding:12px 16px;margin:22px 0;border:0}
.eyebrow{margin:.6em 0 0;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-ink)}
.eyebrow+h1{margin-top:.15em}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:18px 0 8px}
.stats div{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;box-shadow:var(--shadow)}
.stats dt{font-size:.78rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.stats dd{margin:2px 0 0;font-weight:650;line-height:1.35}
.chip{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--brand);background:var(--soft);border-radius:999px;padding:2px 8px;margin-bottom:6px}
.crumbs{font-size:.86rem;color:var(--muted)}.crumbs a{color:var(--muted)}
.gear h3{margin:.1em 0}.gear p{margin:.3em 0 .9em}
.ad{margin:28px 0;min-height:0}
.calc{background:linear-gradient(180deg,var(--card),var(--card)) padding-box;border-top:4px solid var(--accent)}
.fields{display:grid;grid-template-columns:1.4fr 1fr;gap:14px}
label{font-weight:650;display:block;margin:4px 0 6px;font-size:.92rem}
select,input[type=time]{font:inherit;font-size:1rem;width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink)}
select:focus,input:focus,.btn:focus-visible,a:focus-visible{outline:3px solid color-mix(in srgb,var(--accent) 60%,transparent);outline-offset:2px}
.install{border-color:var(--accent);background:var(--accent-soft)}.linkbtn{background:none;border:0;color:var(--muted);text-decoration:underline;cursor:pointer;font-size:.95rem}
footer{border-top:1px solid var(--line);background:var(--bg2);font-size:.88rem;color:var(--muted);padding:26px 0 34px}
footer a{color:var(--muted);margin-right:16px}
@media(max-width:600px){body{font-size:16.5px}.grid{grid-template-columns:1fr 1fr;gap:10px}.grid>li:last-child:nth-child(odd){grid-column:1/-1}.grid a{padding:12px 14px;font-size:.95rem}.stats{grid-template-columns:1fr 1fr}.tl td:first-child{white-space:normal;width:38%}h1{font-size:1.85rem}h2{font-size:1.32rem}.hero{padding:22px 18px;border-radius:18px}.fields{grid-template-columns:1fr}
header.site .wrap{flex-wrap:wrap;padding-top:8px;padding-bottom:6px;gap:4px}nav{width:100%;margin:0 -10px}th,td{padding:10px 11px}.tl td:last-child{padding-left:30px}.tl td:last-child:before{left:11px}}
"""


SW = """// Offline support: same-origin only, so ad and affiliate requests are never cached.
const CACHE = 'nap-__VERSION__';
const PRECACHE = __PRECACHE__;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (req.mode === 'navigate') {
    // Network first for pages, so content updates show up; fall back to cache offline.
    e.respondWith(fetch(req).then(res => {
      const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res;
    }).catch(() => caches.match(req, {ignoreSearch: true}).then(r => r || caches.match('/nap-calculator/'))));
    return;
  }
  // Stale-while-revalidate for assets: serve the cached copy, refresh it in the background.
  e.respondWith(caches.match(req).then(cached => {
    const net = fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    }).catch(() => cached);
    return cached || net;
  }));
});
"""


SW_REGISTER = """<script>if('serviceWorker' in navigator){addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}))}</script>"""

INSTALL_HINT = r"""<div class="card install" id="install" hidden>
<strong>Keep the calculator on your phone</strong>
<p id="install-text">Add it to your home screen. It opens like an app and works offline, even at 3 AM with bad signal.</p>
<p><button class="btn" id="install-btn" type="button" hidden>Add to Home Screen</button> <button type="button" id="install-x" class="linkbtn">No thanks</button></p>
</div>
<script>
(function(){
var box=document.getElementById('install'),btn=document.getElementById('install-btn'),txt=document.getElementById('install-text'),evt=null;
function dismissed(){try{return localStorage.getItem('installHint')==='no'}catch(e){return false}}
var standalone=window.matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
if(standalone||dismissed())return;
var ua=navigator.userAgent,ios=/iphone|ipad|ipod/i.test(ua)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
if(ios){txt.innerHTML='Add it to your home screen: tap the <strong>Share</strong> button in Safari, then <strong>Add to Home Screen</strong>. It opens like an app and works offline.';box.hidden=false}
addEventListener('beforeinstallprompt',function(e){e.preventDefault();evt=e;btn.hidden=false;box.hidden=false});
btn.addEventListener('click',function(){if(!evt)return;evt.prompt();evt.userChoice.finally(function(){evt=null;box.hidden=true})});
document.getElementById('install-x').addEventListener('click',function(){box.hidden=true;try{localStorage.setItem('installHint','no')}catch(e){}});
addEventListener('appinstalled',function(){box.hidden=true});
})();
</script>"""


AGE_HINT = {"bw-1-2w": "Newborn", "bw-3-5w": "About 1 month", "bw-6-7w": "About 6 weeks", "bw-8-12w": "2–3 months",
            "bw-13-15w": "About 3 months", "bw-16-24w": "4–5 months", "bw-25-38w": "6–9 months", "bw-39-52w": "9–12 months"}


CSS_VER = hashlib.sha1(CSS.encode()).hexdigest()[:8]


def kind(text):
    t = text.lower()
    if "down for the night" in t or (t.startswith("bedtime") and "feed" not in t) or "bedtime routine" in t:
        return "night"
    if t.startswith(("nap", "catnap", "evening sleep", "quiet")):
        return "nap"
    if any(w in t for w in ("feed", "milk", "breakfast", "lunch", "snack", "dinner")):
        return "feed"
    if any(w in t for w in ("nap", "sleep", "quiet time")):
        return "nap"
    return "wake"


LEGEND = '<div class="legend"><span><i style="background:var(--feed)"></i>Feed or meal</span><span><i style="background:var(--wake)"></i>Awake</span><span><i style="background:var(--nap)"></i>Nap</span><span><i style="background:var(--night)"></i>Night</span></div>'


def ad_slot():
    if not ADSENSE_CLIENT:
        return "<!-- ad slot: set ADSENSE_CLIENT in build.py -->"
    return f'''<div class="ad"><ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>'''


def gear_box(n=3):
    picks = BOOKS[:2] + GEAR[:n - 1]
    items = "".join(
        f'<li><a href="{esc(amazon_url(q))}" rel="sponsored nofollow noopener" target="_blank">{esc(t)}</a></li>'
        for t, q, _ in picks)
    return f'''<div class="card"><strong>Books and nap helpers parents like</strong><ul>{items}</ul>
<small>See our <a href="/nap-gear/">full nap gear list</a>. As an Amazon Associate we earn from qualifying purchases.</small></div>'''


BW_NOTE = ('<p class="note"><strong>About Babywise and feeding schedules:</strong> The American Academy of Pediatrics recommends feeding babies '
           'when they show hunger cues, and in 1998 it raised concerns that strict schedule-based feeding can lead to poor weight gain, '
           'dehydration and low milk supply. If you use a Babywise-style routine, treat feeding times as flexible, feed your baby whenever '
           'they are hungry, and keep up with weight checks at your pediatrician.</p>')


# Old 0-12 month wake-window pages now forward to the matching Babywise stage.
BW_REDIRECT = {"newborn": "babywise-schedule-weeks-1-2", "2-3m": "babywise-schedule-weeks-8-12",
               "4-5m": "babywise-schedule-weeks-16-24", "6-7m": "babywise-schedule-6-9-months",
               "8-10m": "babywise-schedule-9-12-months"}
TODDLERS = [a for a in AGES if a["key"] not in BW_REDIRECT]


def redirect_page(path, target):
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    url = SITE + target
    with open(os.path.join(d, "index.html"), "w") as f:
        f.write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>
<link rel="canonical" href="{url}"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0; url={target}">
</head><body><p>This page has moved to <a href="{target}">{url}</a>.</p></body></html>''')


def bw_rows(st, first=7 * 60):
    rows = []
    cyc = st["cycles"]
    for i, (off, label, wake, nap) in enumerate(cyc):
        t = first + off
        rows.append((t, fmt_time(t), label + (" and waketime" if nap and nap != "night" else "")))
        if nap == "night":
            rows.append((t + wake, fmt_time(t + wake), "Down for the night"))
        elif nap:
            end = first + cyc[i + 1][0]
            when = fmt_time(t + wake) if nap.startswith("Catnap") else fmt_range(t + wake, end)
            rows.append((t + wake, when, nap))
    for off, label in st["night"]:
        rows.append((first + off, fmt_time(first + off), label))
    return [(a, b) for _, a, b in rows]


BABYWISE_TM = ('<p class="note"><strong>Trademark and affiliation:</strong> Babywise and the titles of the Babywise books are trademarks of their respective owners. '
               'NapSchedule.com is an independent site. It is not affiliated with, sponsored by or endorsed by Gary Ezzo, Robert Bucknam, MD, or their publisher. '
               'We refer to the books by name only to describe and review them, and our schedules are our own summaries, not text or charts from the books.</p>')


DISCLAIMER = '<p class="note">This site shares general information, not medical advice. Every child is different. Talk with your pediatrician about your child\'s sleep, especially if you have concerns about health, growth, or breathing.</p>'


def page(path, title, desc, body, schema=None, crumbs=None):
    url = SITE + path
    ld = []
    ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/"} if path == "/" else None)
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]})
    if schema:
        ld.extend(schema)
    ld = [x for x in ld if x]
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    crumbs_html = ""
    if crumbs and len(crumbs) > 1:
        crumbs_html = '<div class="crumbs">' + " › ".join(
            f'<a href="{u}">{esc(n)}</a>' for n, u in crumbs[:-1]) + f" › {esc(crumbs[-1][0])}</div>"
    adsense_head = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'
                    if ADSENSE_CLIENT else "")
    doc = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap">
<link rel="stylesheet" href="/style.css?v={CSS_VER}">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#faf7f2" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#12151f" media="(prefers-color-scheme: dark)">
<link rel="apple-touch-icon" href="/icons/icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Nap Day">
{adsense_head}{ld_html}
</head><body>
<header class="site"><div class="wrap"><a class="logo" href="/"><svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="16" fill="#2f4a75"/><path d="M37 15a17 17 0 1 0 12 28A15 15 0 0 1 37 15z" fill="#e3a564"/></svg><span class="wm">Nap<b>Schedule</b></span></a>
<nav><a href="/schedules/">By age</a><a href="/babywise/">Babywise</a><a href="/nap-calculator/">Calculator</a><a href="/guides/">Guides</a></nav></div></header>
<main><div class="wrap">{crumbs_html}
{body}
</div></main>
<footer><div class="wrap"><a href="/about/">About</a><a href="/privacy/">Privacy</a><a href="/disclaimer/">Disclaimer</a><a href="/nap-gear/">Nap gear</a>
<p>© {datetime.date.today().year} NapSchedule.com · General information only, not medical advice. Babywise is a trademark of its owners; this site is independent and not affiliated with or endorsed by the Babywise authors or publisher.</p></div></footer>
{SW_REGISTER}
</body></html>"""
    if path.endswith(".html"):
        fn = os.path.join(OUT, path.strip("/"))
    else:
        d = os.path.join(OUT, path.strip("/"))
        os.makedirs(d, exist_ok=True)
        fn = os.path.join(d, "index.html")
    with open(fn, "w") as f:
        f.write(doc)
    return path


def faq_schema(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def faq_html(faq):
    return "<h2>Frequently asked questions</h2>" + "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in faq)


def article_schema(title, desc, path):
    return {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
            "mainEntityOfPage": SITE + path, "dateModified": TODAY,
            "author": {"@type": "Organization", "name": NAME}, "publisher": {"@type": "Organization", "name": NAME}}


# ---------------------------------------------------------------------------
def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    pages = []
    H = ("Home", "/")

    # Age pages
    for i, a in enumerate(AGES):
        path = f"/schedules/{a['slug']}/"
        if a["key"] in BW_REDIRECT:
            redirect_page(path, f"/babywise/{BW_REDIRECT[a['key']]}/")
            continue
        rows = "".join(f'<tr class="{kind(x)}"><td>{esc(t)}</td><td>{esc(x)}</td></tr>' for t, x in schedule_rows(a))
        prev_a = AGES[i - 1] if i > 0 else None
        next_a = AGES[i + 1] if i + 1 < len(AGES) else None
        pn = ""
        if prev_a and prev_a["key"] in BW_REDIRECT:
            pn += '<a href="/babywise/babywise-schedule-9-12-months/">← Babywise 9–12 months</a>'
        elif prev_a:
            pn += f'<a href="/schedules/{prev_a["slug"]}/">← {esc(prev_a["label"])}</a>'
        if next_a:
            pn += f'<a style="float:right" href="/schedules/{next_a["slug"]}/">{esc(next_a["label"])} →</a>'
        tips = "".join(f"<li>{t}</li>" for t in a["tips"])
        extra = ""
        if a["key"] == "3-5y":
            extra = '<h3>Sample day without a nap</h3><table class="tl"><thead><tr><th>Time</th><th>What happens</th></tr></thead><tbody><tr class="wake"><td>7:00 AM</td><td>Wake up</td></tr><tr class="nap"><td>1:00 – 2:00 PM</td><td>Quiet time in their room</td></tr><tr class="night"><td>6:45 – 7:30 PM</td><td>Bedtime (earlier than on nap days)</td></tr></tbody></table>'
        if a["key"] == "newborn":
            extra = "<p><em>Newborn days rarely look this tidy. Use this as a rough picture of how often your baby may sleep, not a schedule to enforce.</em></p>"
        body = f"""<p class="eyebrow">Toddler nap schedule</p><h1>{esc(a['label'])} nap schedule</h1>
<p class="lead">{esc(a['desc'])}</p>
<dl class="stats">
<div><dt>Naps a day</dt><dd>{a['naps_count']}</dd></div>
<div><dt>Total sleep</dt><dd>{a['total']}</dd></div>
<div><dt>Awake between sleeps</dt><dd>{a['ww_range']}</dd></div>
<div><dt>Daytime sleep</dt><dd>{a['day_sleep']}</dd></div>
<div><dt>Bedtime</dt><dd>{a['bedtime']}</dd></div></dl>
{a['intro']}
<p><strong>Following Babywise?</strong> The same predictable rhythm carries on into toddlerhood: consistent wake-up, meals, naps and bedtime at about the same times every day. The Ezzos cover this stage in <a href="{esc(amazon_url(BOOKS[2][1]))}" rel="sponsored nofollow noopener" target="_blank"><em>On Becoming Pretoddlerwise</em></a> and <a href="{esc(amazon_url(BOOKS[3][1]))}" rel="sponsored nofollow noopener" target="_blank"><em>On Becoming Toddlerwise</em></a>.</p>
{ad_slot()}
<h2>Sample {esc(a['short'])} schedule</h2>
<p>Based on a 7:00 AM wake-up. Your times will shift with your baby's wake time. <a href="/nap-calculator/?age={a['key']}">Get times for your day →</a></p>
<table class="tl"><thead><tr><th>Time</th><th>What happens</th></tr></thead><tbody>{rows}</tbody></table>
{LEGEND}
{extra}
<h2>Tips for this age</h2><ul>{tips}</ul>
<h2>What's next</h2><p>{a['next']}</p>
{gear_box()}
{faq_html(a['faq'])}
{DISCLAIMER}
<p>{pn}</p>"""
        pages.append(page(path, a["title"], a["desc"], body,
                          schema=[article_schema(a["title"], a["desc"], path), faq_schema(a["faq"])],
                          crumbs=[H, ("Schedules by age", "/schedules/"), (a["label"], path)]))

    # Schedules hub
    bgrid0 = "".join(f'<li><a href="/babywise/{st["slug"]}/"><span class="chip">{esc(AGE_HINT[st["key"]])}</span> <span class="t">{esc(st["label"].split(" (")[0])}</span><small>{st["naps"]} {"nap" if st["naps"] == "1" else "naps"} a day</small></a></li>' for st in BW_STAGES)
    grid = "".join(f'<li><a href="/schedules/{a["slug"]}/"><span class="chip">Toddler</span> <span class="t">{esc(a["label"])}</span><small>{a["naps_count"].split(" (")[0]} {"nap" if a["naps_count"] == "1" else "naps"} a day</small></a></li>' for a in TODDLERS)
    summary = "".join(f'<tr><td><a href="/schedules/{a["slug"]}/">{esc(a["label"])}</a></td><td>{a["naps_count"]}</td><td>{a["ww_range"]}</td><td>{a["total"]}</td></tr>' for a in TODDLERS)
    body = f"""<h1>Nap schedules by age</h1>
<p class="lead">Babywise eat-wake-sleep schedules for the first year, then toddler nap schedules up to age 5.</p>
<h2>Birth to 12 months: Babywise schedules</h2>
<ul class="grid g4">{bgrid0}</ul>
<p><a href="/babywise/">How the Babywise routine works →</a></p>
<h2>12 months to 5 years: toddler naps</h2>
<ul class="grid g5">{grid}</ul>
<table><thead><tr><th>Age</th><th>Naps</th><th>Time awake between sleeps</th><th>Total sleep / 24h</th></tr></thead><tbody>{summary}</tbody></table>
<p><small>First-year schedules are summarized from {esc(BOOK)}. Toddler sleep totals follow the American Academy of Sleep Medicine recommendations endorsed by the American Academy of Pediatrics.</small></p>
{DISCLAIMER}"""
    pages.append(page("/schedules/", "Baby & Toddler Nap Schedules by Age: Babywise to Age 5",
                      "Babywise eat-wake-sleep schedules for birth to 12 months, plus toddler nap schedules to age 5: naps, feeds, total sleep and sample days.",
                      body, crumbs=[H, ("Schedules by age", "/schedules/")]))

    # Guides
    for g in GUIDES:
        path = f"/guides/{g['slug']}/"
        body = f"""<h1>{esc(g['h1'])}</h1><p class="lead">{esc(g['desc'])}</p>
{g['body']}
{ad_slot()}
{gear_box()}
{faq_html(g['faq'])}
{DISCLAIMER}"""
        pages.append(page(path, g["title"], g["desc"], body,
                          schema=[article_schema(g["title"], g["desc"], path), faq_schema(g["faq"])],
                          crumbs=[H, ("Guides", "/guides/"), (g["h1"], path)]))
    grid = "".join(f'<li><a href="/guides/{g["slug"]}/">{esc(g["h1"])}<small>{esc(g["desc"][:90])}…</small></a></li>' for g in GUIDES)
    pages.append(page("/guides/", "Baby & Toddler Nap Guides", "Practical guides to wake windows, sleep regressions, nap transitions, short naps, and safe sleep.",
                      f'<h1>Nap guides</h1><p class="lead">Short, practical guides for the trickiest parts of naps.</p><ul class="grid g4">{grid}</ul>',
                      crumbs=[H, ("Guides", "/guides/")]))

    # Babywise section
    BWH = ("Babywise schedules", "/babywise/")
    for i, st in enumerate(BW_STAGES):
        path = f"/babywise/{st['slug']}/"
        rows = "".join(f'<tr class="{kind(x)}"><td>{esc(t)}</td><td>{esc(x)}</td></tr>' for t, x in bw_rows(st))
        tips = "".join(f"<li>{t}</li>" for t in st["tips"])
        pn = ""
        if i > 0:
            pn += f'<a href="/babywise/{BW_STAGES[i-1]["slug"]}/">← {esc(BW_STAGES[i-1]["label"])}</a>'
        if i + 1 < len(BW_STAGES):
            pn += f'<a style="float:right" href="/babywise/{BW_STAGES[i+1]["slug"]}/">{esc(BW_STAGES[i+1]["label"])} →</a>'
        body = f"""<p class="eyebrow">Babywise-style schedule · {esc(AGE_HINT[st['key']])}</p>
<h1>{esc(st['label'].split(' (')[0])} eat-wake-sleep schedule</h1>
<p class="lead">{esc(st['desc'])}</p>
<dl class="stats">
<div><dt>Naps a day</dt><dd>{st['naps']}</dd></div>
<div><dt>Total sleep</dt><dd>{st['sleep']}</dd></div>
<div><dt>Feeds a day</dt><dd>{st['feeds']}</dd></div>
<div><dt>Between feeds</dt><dd>{st['interval']}</dd></div>
<div><dt>Waketime (our estimate)</dt><dd>{st['waketime']}</dd></div></dl>
<p><small>Naps, total sleep and feed counts are from {esc(BOOK)}, summarized in our own words. Waketime is our estimate.</small></p>
{st['intro']}
{ad_slot()}
<h2>Sample eat-wake-sleep day</h2>
<p>Based on a 7:00 AM first feed. <a href="/nap-calculator/?method=bw&amp;age={st['key']}">Get times for your day →</a></p>
<table class="tl"><thead><tr><th>Time</th><th>What happens</th></tr></thead><tbody>{rows}</tbody></table>
{LEGEND}
<h2>Tips for this stage</h2><ul>{tips}</ul>
{gear_box()}
{BW_NOTE}
{BABYWISE_TM}
{DISCLAIMER}
<p>{pn}</p>"""
        pages.append(page(path, st["title"], st["desc"], body, schema=[article_schema(st["title"], st["desc"], path)],
                          crumbs=[H, BWH, (st["label"], path)]))
    bgrid = "".join(f'<li><a href="/babywise/{st["slug"]}/"><span class="chip">{esc(AGE_HINT[st["key"]])}</span> <span class="t">{esc(st["label"].split(" (")[0])}</span><small>{st["naps"]} {"nap" if st["naps"] == "1" else "naps"} a day</small></a></li>' for st in BW_STAGES)
    btab = "".join(f'<tr><td><a href="/babywise/{st["slug"]}/">{esc(st["label"])}</a></td><td>{st["naps"]}</td><td>{st["sleep"]}</td><td>{esc(st["feeds"])}</td></tr>' for st in BW_STAGES)
    books = "".join(f'<li><a href="{esc(amazon_url(q))}" rel="sponsored nofollow noopener" target="_blank">{esc(t)}</a>: {esc(d)}</li>' for t, q, d in BOOKS)
    bw_faq = [("What is the Babywise method?", "Babywise is a parent-directed routine from the book On Becoming Babywise by Gary Ezzo and Robert Bucknam, MD. Each part of the day follows the same order: feed, waketime, then sleep. Feeds are spaced roughly 2.5 to 3 hours apart in the early weeks, and feeds gradually merge as the baby grows."),
              ("When do Babywise babies sleep through the night?", "The authors say many babies on the routine sleep through the night somewhere around 8 to 12 weeks. Many healthy babies take longer, and night feeds should continue as long as your baby is hungry."),
              ("Is Babywise safe?", "The AAP recommends feeding on hunger cues and has warned that rigid schedules can cause poor weight gain and low milk supply. If you follow a Babywise-style routine, keep it flexible, feed your baby when hungry, and track weight gain with your pediatrician.")]
    body = f"""<h1>Babywise schedules by age</h1>
<p class="lead">Eat-wake-sleep routines from birth to 12 months, based on <em>On Becoming Babywise</em>. Pick your baby's age for feed times, naps and a sample day.</p>
<ul class="grid g4">{bgrid}</ul>
<h2>How the Babywise routine works</h2>
<p>Babywise organizes the day into repeating <strong>feed, waketime, sleep</strong> cycles. Instead of feeding a baby to sleep, you feed after they wake, enjoy some awake time, then put them down for a nap. The authors call this parent-directed feeding: the parent sets a rhythm, while still watching the baby's hunger cues.</p>
<p>Over the first year, feeds gradually <strong>merge</strong>. Night feeds go first, then the late-evening feed, then a daytime feed as solids arrive, until your baby is eating family meals with two naps a day.</p>
<h2>Babywise chart at a glance</h2>
<table><thead><tr><th>Age</th><th>Naps</th><th>Total sleep</th><th>Feeds</th></tr></thead><tbody>{btab}</tbody></table>
<p><small>Summarized from {esc(BOOK)}.</small></p>
<h2>Signs your baby is eating enough</h2>
<ul><li>At least 8 feeds a day in the first few weeks, 7 or more by about 5 weeks.</li>
<li>Plenty of wet diapers (about 6 or more a day after the first week) with pale urine.</li>
<li>Regular stools and steady weight gain at checkups.</li>
<li>A baby who seems satisfied after feeds and is alert during waketime.</li></ul>
<p>If any of these are off, feed more often and call your pediatrician.</p>
{ad_slot()}
<h2>The Babywise books</h2><ul>{books}</ul>
<p><small>As an Amazon Associate we earn from qualifying purchases.</small></p>
<p><a class="btn" href="/nap-calculator/?method=bw">Build a Babywise day in the calculator</a></p>
{faq_html(bw_faq)}
{BW_NOTE}
{BABYWISE_TM}
{DISCLAIMER}"""
    pages.append(page("/babywise/", "Babywise Schedule by Age: Eat-Wake-Sleep Routines 0–12 Months",
                      "Babywise-style eat-wake-sleep schedules from birth to 12 months: feeds, waketimes, naps and sample days, based on On Becoming Babywise.",
                      body, schema=[faq_schema(bw_faq)], crumbs=[H, BWH]))

    # Calculator
    calc_data = {}
    for st in BW_STAGES:
        calc_data[st["key"]] = {"bw": 1, "label": "Babywise " + st["label"], "path": f"/babywise/{st['slug']}/",
                                "cycles": [list(c) for c in st["cycles"]], "night": [list(n) for n in st["night"]]}
    for a in TODDLERS:
        calc_data[a["key"]] = {"bw": 0, "label": a["label"], "path": f"/schedules/{a['slug']}/", "ww": a["ww"], "naps": a["naps"]}
    opts = ('<optgroup label="Babywise (birth to 12 months)">' + "".join(f'<option value="{st["key"]}">{esc(st["label"])}</option>' for st in BW_STAGES)
            + '</optgroup><optgroup label="Toddlers">' + "".join(f'<option value="{a["key"]}">{esc(a["label"])}</option>' for a in TODDLERS) + '</optgroup>')
    calc_faq = [("How does the Babywise calculator work?", "For babies under 12 months, it lays out eat-wake-sleep cycles from your first feed of the day, using the feed spacing and number of naps described in On Becoming Babywise for your baby's age. For toddlers, it uses typical awake times and nap lengths."),
                ("What if my baby is hungry early?", "Feed your baby. The times are a plan for the day, not a rule. Babywise itself says to feed a hungry baby, and the AAP recommends feeding on hunger cues."),
                ("What if a nap runs short or long?", "Start the next feed at about the planned time if you can, or shift the rest of the day by the same amount. Consistency over several days matters more than any single nap.")]
    body = f"""<p class="eyebrow">Free calculator</p><h1>Plan your baby's day</h1>
<p class="lead">Pick an age and the first feed of the morning. You'll get a full Babywise-style eat-wake-sleep day, or a nap plan for toddlers.</p>
<div class="card calc">
<div class="fields"><div><label for="age">Baby's age</label><select id="age">{opts}</select></div>
<div><label for="wake" id="wake-label">First feed of the day</label><input type="time" id="wake" value="07:00"></div></div>
<p><button class="btn" id="go" type="button">Build my schedule</button></p>
<div id="out" aria-live="polite"></div>
</div>
{INSTALL_HINT}
<script>
const D={json.dumps(calc_data)};const LG={json.dumps(LEGEND)};
function f(m){{m=((m%1440)+1440)%1440;let h=Math.floor(m/60),mm=m%60,ap=h<12?'AM':'PM';h=h%12||12;return h+':'+String(mm).padStart(2,'0')+' '+ap}}
function d(m){{const h=Math.floor(m/60),x=m%60;return (h?h+' hr'+(h>1?'s':''):'')+(h&&x?' ':'')+(x?x+' min':'')}}
function k(b){{const t=b.toLowerCase();if(t.includes('down for the night')||(t.startsWith('bedtime')&&!t.includes('feed'))||t.includes('bedtime routine'))return 'night';if(/^(nap|catnap|evening sleep|quiet)/.test(t))return 'nap';if(/feed|milk|breakfast|lunch|snack|dinner/.test(t))return 'feed';if(/nap|sleep|quiet time/.test(t))return 'nap';return 'wake'}}
function rg(a,b){{const x=f(a),y=f(b);return x.slice(-2)===y.slice(-2)?x.slice(0,-3)+'–'+y:x+'–'+y}}
function row(a,b){{return '<tr class="'+k(b)+'"><td>'+a+'</td><td>'+b+'</td></tr>'}}
function run(){{const a=D[document.getElementById('age').value];const v=document.getElementById('wake').value||'07:00';let [h,m]=v.split(':').map(Number);const s0=h*60+m;let t=s0;
document.getElementById('wake-label').textContent=a.bw?'First feed of the day':'Woke up at';
let r='<table class="tl"><thead><tr><th>Time</th><th>What happens</th></tr></thead><tbody>';
if(a.bw){{a.cycles.forEach((c,i)=>{{const [off,lab,wk,nap]=c;const ft=s0+off;r+=row(f(ft),lab+(nap&&nap!=='night'?' and waketime':''));
if(nap==='night')r+=row(f(ft+wk),'Down for the night');else if(nap)r+=row(nap.startsWith('Catnap')?f(ft+wk):rg(ft+wk,s0+a.cycles[i+1][0]),nap)}});
a.night.forEach(n=>{{r+=row(f(s0+n[0]),n[1])}});r+='</tbody></table>'+LG;
r+='<p>Feed times are a guide. If your baby is hungry sooner, feed them. <a href="'+a.path+'">See the full '+a.label+' schedule →</a></p>'}}
else{{r+=row(f(t),'Wake up');a.naps.forEach((n,i)=>{{t+=a.ww[i];r+=row(rg(t,t+n),'Nap '+(i+1)+' (about '+d(n)+')');t+=n}});
t+=a.ww[a.naps.length];r+=row(f(t),'Bedtime')+'</tbody></table>'+LG;
r+='<p>These are estimates. Watch for sleepy cues and adjust by 15 minutes or so. <a href="'+a.path+'">See the full '+a.label+' guide →</a></p>'}}
document.getElementById('out').innerHTML=r}}
const OLD={{"newborn":"bw-1-2w","2-3m":"bw-8-12w","4-5m":"bw-16-24w","6-7m":"bw-25-38w","8-10m":"bw-39-52w"}};
let q=new URLSearchParams(location.search).get('age');if(!q){{try{{q=localStorage.getItem('napAge')}}catch(e){{}}}}if(q&&OLD[q])q=OLD[q];if(q&&D[q])document.getElementById('age').value=q;
document.getElementById('age').addEventListener('change',e=>{{try{{localStorage.setItem('napAge',e.target.value)}}catch(_){{}}}});
document.getElementById('go').addEventListener('click',run);document.getElementById('age').addEventListener('change',run);document.getElementById('wake').addEventListener('change',run);run();
</script>
{ad_slot()}
<h2>How to use these times</h2>
<p>For babies under 12 months, each row follows the Babywise order: feed, waketime, then nap. Start the day with the first feed at the same time each morning, and the rest of the day tends to fall into place. Waketime lengths are our estimates within the book's feed spacing. Real babies vary, so treat this as a plan, not a rule.</p>
<p>New to the routine? Read <a href="/babywise/">how Babywise works</a>.</p>
{faq_html(calc_faq)}
{BW_NOTE}
{BABYWISE_TM}
{DISCLAIMER}"""
    pages.append(page("/nap-calculator/", "Babywise-Style Schedule Calculator: Eat-Wake-Sleep Day Planner",
                      "Free Babywise schedule calculator: enter your baby's age and first feed time to get feed, waketime and nap times for the day, plus toddler nap plans.",
                      body, schema=[faq_schema(calc_faq), {"@context": "https://schema.org", "@type": "WebApplication", "name": "Eat-Wake-Sleep Schedule Calculator",
                                                          "url": SITE + "/nap-calculator/", "applicationCategory": "LifestyleApplication",
                                                          "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}],
                      crumbs=[H, ("Nap calculator", "/nap-calculator/")]))

    # Gear
    items = "".join(f'<div class="card gear"><h3>{esc(t)}</h3><p>{esc(p)}</p><a class="btn" href="{esc(amazon_url(q))}" rel="sponsored nofollow noopener" target="_blank">See options on Amazon</a></div>' for t, q, p in GEAR)
    bitems = "".join(f'<div class="card gear"><h3>{esc(t)}</h3><p>{esc(p)}</p><a class="btn" href="{esc(amazon_url(q))}" rel="sponsored nofollow noopener" target="_blank">See it on Amazon</a></div>' for t, q, p in BOOKS)
    body = f"""<h1>Babywise books and nap gear</h1>
<p class="lead">The books behind the eat-wake-sleep routine, plus the few pieces of gear that make the biggest difference for naps.</p>
<p class="note">As an Amazon Associate we earn from qualifying purchases. It doesn't change the price you pay.</p>
<h2>The Babywise books</h2>
{bitems}
<h2>Nap gear</h2>
{items}
<p>Whatever you buy, keep the crib bare: a firm mattress and fitted sheet only. See <a href="/guides/safe-sleep-basics/">safe sleep basics</a>.</p>"""
    pages.append(page("/nap-gear/", "Babywise Books and Baby Nap Essentials", "The Babywise book series by age, plus the nap essentials that make the biggest difference: white noise, blackout shades, sleep sacks and toddler clocks.",
                      body, crumbs=[H, ("Nap gear", "/nap-gear/")]))

    # Static info pages
    pages.append(page("/about/", "About NapSchedule", "About NapSchedule.com: simple, practical nap schedules for babies and toddlers.",
                      """<h1>About NapSchedule</h1><p>NapSchedule.com is a simple, no-nonsense reference for baby and toddler nap schedules. Our goal is to give tired parents clear, practical answers: how many naps, how long between them, and what a typical day looks like at each age.</p>
<p>Our first-year schedules follow the eat-wake-sleep routine described in <em>On Becoming Babywise</em> (25th Anniversary Edition) by Gary Ezzo and Robert Bucknam, MD, summarized in our own words. Toddler schedules use the total sleep recommendations from the American Academy of Sleep Medicine (endorsed by the American Academy of Pediatrics), and our safety advice follows the AAP's safe sleep recommendations. We are not affiliated with the Babywise authors or publisher.</p>
<p>Because the AAP recommends feeding babies on hunger cues, we always present Babywise feed times as a flexible guide. Your baby's hunger and growth come first.</p>
<p>We keep the site free with advertising and affiliate links. See our <a href="/privacy/">privacy policy</a> and <a href="/disclaimer/">disclaimer</a>.</p>""" + DISCLAIMER))
    pages.append(page("/disclaimer/", "Disclaimer", "Medical and affiliate disclaimer for NapSchedule.com.",
                      """<h1>Disclaimer</h1><h2>Not medical advice</h2><p>The content on NapSchedule.com is for general informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always ask your pediatrician or another qualified health provider about your child's health and sleep. If you think your child may have a medical emergency, call your doctor or emergency services immediately.</p>
<h2>Babywise</h2><p>Babywise and the titles of the Babywise books are trademarks of their respective owners. NapSchedule.com is an independent site and is not affiliated with, sponsored by or endorsed by Gary Ezzo, Robert Bucknam, MD, or their publisher. We mention the books by name to describe and review them. Our "Babywise-style" schedules are our own summaries of the general approach and are not reproduced from the books. For the authors' own guidance, read the books.</p><p>Following any feeding or sleep routine, including a Babywise-style routine, is your decision. Feed your baby whenever they show hunger, watch their weight gain and diapers, and follow your pediatrician's advice over anything on this site. We accept no liability for how the information here is used.</p>
<h2>Affiliate disclosure</h2><p>NapSchedule.com is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com. As an Amazon Associate we earn from qualifying purchases. This doesn't change the price you pay.</p>"""))
    pages.append(page("/privacy/", "Privacy Policy", "Privacy policy for NapSchedule.com.",
                      f"""<h1>Privacy policy</h1><p>Last updated: {TODAY}</p>
<p>NapSchedule.com does not ask you to create an account and does not collect personal information through forms. The nap calculator runs entirely in your browser; the age and times you enter are not sent to us.</p>
<h2>Advertising</h2><p>We may use third-party advertising companies, such as Google AdSense, to serve ads. These companies may use cookies to serve ads based on your prior visits to this and other websites. Google's use of advertising cookies enables it and its partners to serve ads based on your visits to this site and/or other sites on the Internet. You may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" rel="noopener" target="_blank">Google Ads Settings</a>. Learn more at <a href="https://policies.google.com/technologies/partner-sites" rel="noopener" target="_blank">how Google uses information from sites that use its services</a>.</p>
<h2>Affiliate links</h2><p>Some links go to Amazon. If you buy through them, Amazon may use cookies to attribute the purchase to us. See the <a href="/disclaimer/">disclaimer</a>.</p>
<h2>Hosting</h2><p>This site is hosted on GitHub Pages, which may log basic technical information such as IP addresses for security purposes.</p>
<h2>Children</h2><p>This site is written for parents and caregivers and is not directed to children under 13.</p>"""))

    # Home
    bgrid = "".join(f'<li><a href="/babywise/{st["slug"]}/"><span class="chip">{esc(AGE_HINT[st["key"]])}</span> <span class="t">{esc(st["label"].split(" (")[0])}</span><small>{st["naps"]} {"nap" if st["naps"] == "1" else "naps"} a day</small></a></li>' for st in BW_STAGES)
    grid = "".join(f'<li><a href="/schedules/{a["slug"]}/"><span class="chip">Toddler</span> <span class="t">{esc(a["label"])}</span><small>{a["naps_count"].split(" (")[0]} {"nap" if a["naps_count"] == "1" else "naps"} a day</small></a></li>' for a in TODDLERS)
    ggrid = "".join(f'<li><a href="/guides/{g["slug"]}/">{esc(g["h1"])}</a></li>' for g in GUIDES)
    home_faq = [("What is a Babywise schedule?", "A Babywise schedule follows the routine from On Becoming Babywise: the day repeats in feed, waketime, sleep cycles, with feeds about 2.5 to 3 hours apart in the early weeks and fewer, fuller feeds as the baby grows."),
                ("How many naps does a Babywise baby take?", "According to the book, about 5 to 6 naps in the first weeks, 4 to 5 around 2 to 3 months, 3 to 4 from about 3 to 6 months, 2 to 3 from 6 to 9 months, and 2 by 9 to 12 months."),
                ("When do toddlers drop to one nap?", "Most toddlers move from two naps to one between 13 and 18 months.")]
    body = f"""<section class="hero"><h1>Babywise schedules, made simple</h1>
<p class="lead">Eat-wake-sleep routines for every stage of the first year, toddler nap schedules to age 5, and a free calculator that builds your baby's day from the first feed.</p>
<p><a class="btn" href="/nap-calculator/">Plan my baby's day</a></p></section>
<h2>Babywise schedules: birth to 12 months</h2><ul class="grid g4">{bgrid}</ul>
<p><a href="/babywise/">New to Babywise? Start here →</a></p>
{ad_slot()}
<h2>Toddler nap schedules</h2><ul class="grid g5">{grid}</ul>
<h2>Guides</h2><ul class="grid g4">{ggrid}</ul>
{gear_box()}
{faq_html(home_faq)}
{BW_NOTE}
{BABYWISE_TM}
{DISCLAIMER}"""
    pages.append(page("/", "Babywise Schedule by Age + Calculator | NapSchedule",
                      "Babywise eat-wake-sleep schedules from birth to 12 months, toddler nap schedules to age 5, and a free Babywise schedule calculator.",
                      body, schema=[faq_schema(home_faq)]))

    # 404
    page("/404.html", "Page not found", "Page not found.",
         '<h1>Page not found</h1><p>Try the <a href="/schedules/">nap schedules by age</a> or the <a href="/nap-calculator/">nap calculator</a>.</p>')

    # Support files
    with open(os.path.join(OUT, "style.css"), "w") as f:
        f.write(CSS.strip())
    with open(os.path.join(OUT, "favicon.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#3d5a80"/><path d="M40 14a20 20 0 1 0 10 34A18 18 0 0 1 40 14z" fill="#e0a96d"/></svg>')
    shutil.copytree("static/icons", os.path.join(OUT, "icons"))
    shutil.copy("static/icon.svg", os.path.join(OUT, "icons", "icon.svg"))
    manifest = {
        "name": "NapSchedule Eat-Wake-Sleep Planner", "short_name": "Nap Day",
        "description": "Plan your baby's eat-wake-sleep day by age, plus toddler nap times.",
        "id": "/nap-calculator/", "start_url": "/nap-calculator/?source=pwa", "scope": "/",
        "display": "standalone", "background_color": "#fbf8f3", "theme_color": "#3d5a80",
        "icons": [
            {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [{"name": "Babywise schedules by age", "url": "/babywise/"}],
    }
    with open(os.path.join(OUT, "manifest.webmanifest"), "w") as f:
        json.dump(manifest, f, indent=1)
    precache = ["/", "/nap-calculator/", "/schedules/", f"/style.css?v={CSS_VER}", "/favicon.svg", "/manifest.webmanifest",
                "/icons/icon-192.png", "/icons/icon-512.png", "/icons/icon-180.png"] + [p for p in pages if p.startswith(("/schedules/", "/babywise/"))]
    version = hashlib.sha1("".join(open(os.path.join(dp, fn), "rb").read().hex() for dp, _, fns in sorted(os.walk(OUT)) for fn in sorted(fns)).encode()).hexdigest()[:10]
    with open(os.path.join(OUT, "sw.js"), "w") as f:
        f.write(SW.replace("__VERSION__", version).replace("__PRECACHE__", json.dumps(sorted(set(precache)))))
    with open(os.path.join(OUT, "CNAME"), "w") as f:
        f.write("napschedule.com")
    with open(os.path.join(OUT, ".nojekyll"), "w") as f:
        f.write("")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    if ADSENSE_CLIENT:
        with open(os.path.join(OUT, "ads.txt"), "w") as f:
            f.write(f"google.com, {ADSENSE_CLIENT.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n")
    urls = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in sorted(pages))
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    print(f"Built {len(pages)} pages into {OUT}/")


if __name__ == "__main__":
    build()
