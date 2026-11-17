#!/usr/bin/env python3
"""Static site generator for napschedule.com. Output goes to docs/ (served by GitHub Pages).

Monetization settings: fill these in, run `python3 build.py`, commit, push.
"""
import json, os, shutil, html, datetime, hashlib
from content_ages import AGES
from content_guides import GUIDES

# ---- Monetization config -------------------------------------------------
AMAZON_TAG = ""        # Amazon Associates tracking ID, e.g. "napschedule-20"
ADSENSE_CLIENT = ""    # AdSense publisher ID, e.g. "ca-pub-1234567890123456"
# --------------------------------------------------------------------------

SITE = "https://napschedule.com"
NAME = "NapSchedule"
OUT = "docs"
TODAY = datetime.date.today().isoformat()

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
        rows.append((f"{fmt_time(t)} – {fmt_time(t + nap)}", f"Nap {i + 1} ({fmt_dur(nap)})"))
        t += nap
    t += age["ww"][len(age["naps"])]
    rows.append((fmt_time(t), "Bedtime (start routine 20–30 minutes earlier)"))
    return rows


# ---------------------------------------------------------------------------
CSS = """
:root{--bg:#fbf8f3;--card:#fff;--ink:#22262e;--muted:#5d6472;--line:#e7e1d6;--brand:#3d5a80;--brand2:#e0a96d;--soft:#eef2f8}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--brand)}a:hover{color:#253b57}
.wrap{max-width:820px;margin:0 auto;padding:0 18px}
header.site{background:var(--card);border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding-top:12px;padding-bottom:12px}
.logo{font-weight:800;font-size:1.25rem;text-decoration:none;color:var(--ink)}.logo span{color:var(--brand2)}
nav a{margin-left:16px;text-decoration:none;font-weight:600;font-size:.95rem}nav a:first-child{margin-left:0}
main{padding:28px 0 40px}
h1{font-size:2rem;line-height:1.2;margin:.2em 0 .4em}h2{font-size:1.4rem;margin-top:1.8em}h3{font-size:1.12rem;margin-top:1.4em}
.lead{font-size:1.1rem;color:var(--muted)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:1em 0;font-size:.97rem}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:var(--soft)}tr:last-child td{border-bottom:0}
.glance td:first-child{font-weight:600;width:42%}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;padding:0;list-style:none}
.grid a{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;font-weight:600}
.grid a small{display:block;font-weight:400;color:var(--muted)}
.btn{display:inline-block;background:var(--brand);color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:700;border:0;cursor:pointer;font-size:1rem}
.btn:hover{background:#2c4462;color:#fff}
.note{font-size:.88rem;color:var(--muted);border-left:3px solid var(--brand2);padding:4px 12px;margin:24px 0}
.crumbs{font-size:.88rem;color:var(--muted)}.crumbs a{color:var(--muted)}
.gear h3{margin:.2em 0}.gear p{margin:.3em 0 .6em}
.ad{margin:24px 0;min-height:0}
.install{border-color:var(--brand2);background:#fff8ee}.linkbtn{background:none;border:0;color:var(--muted);text-decoration:underline;cursor:pointer;font-size:.95rem}
label{font-weight:600;display:block;margin:10px 0 4px}
select,input[type=time]{font-size:1rem;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:#fff;min-width:220px;max-width:100%}
footer{border-top:1px solid var(--line);background:var(--card);font-size:.9rem;color:var(--muted);padding:20px 0}
footer a{color:var(--muted);margin-right:14px}
@media(max-width:560px){h1{font-size:1.6rem}nav a{margin-left:12px}}
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
  e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  })));
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


def ad_slot():
    if not ADSENSE_CLIENT:
        return "<!-- ad slot: set ADSENSE_CLIENT in build.py -->"
    return f'''<div class="ad"><ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>'''


def gear_box(n=3):
    items = "".join(
        f'<li><a href="{esc(amazon_url(q))}" rel="sponsored nofollow noopener" target="_blank">{esc(t)}</a></li>'
        for t, q, _ in GEAR[:n])
    return f'''<div class="card"><strong>Nap helpers parents like</strong><ul>{items}</ul>
<small>See our <a href="/nap-gear/">full nap gear list</a>. As an Amazon Associate we earn from qualifying purchases.</small></div>'''


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
<link rel="stylesheet" href="/style.css">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#3d5a80">
<link rel="apple-touch-icon" href="/icons/icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Nap Times">
{adsense_head}{ld_html}
</head><body>
<header class="site"><div class="wrap"><a class="logo" href="/">Nap<span>Schedule</span></a>
<nav><a href="/schedules/">By age</a><a href="/nap-calculator/">Calculator</a><a href="/guides/">Guides</a></nav></div></header>
<main><div class="wrap">{crumbs_html}
{body}
</div></main>
<footer><div class="wrap"><a href="/about/">About</a><a href="/privacy/">Privacy</a><a href="/disclaimer/">Disclaimer</a><a href="/nap-gear/">Nap gear</a>
<p>© {datetime.date.today().year} NapSchedule.com · General information only, not medical advice.</p></div></footer>
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
        rows = "".join(f"<tr><td>{esc(t)}</td><td>{esc(x)}</td></tr>" for t, x in schedule_rows(a))
        prev_a = AGES[i - 1] if i > 0 else None
        next_a = AGES[i + 1] if i + 1 < len(AGES) else None
        pn = ""
        if prev_a:
            pn += f'<a href="/schedules/{prev_a["slug"]}/">← {esc(prev_a["label"])}</a>'
        if next_a:
            pn += f'<a style="float:right" href="/schedules/{next_a["slug"]}/">{esc(next_a["label"])} →</a>'
        tips = "".join(f"<li>{t}</li>" for t in a["tips"])
        extra = ""
        if a["key"] == "3-5y":
            extra = '<h3>Sample day without a nap</h3><table><thead><tr><th>Time</th><th>What happens</th></tr></thead><tbody><tr><td>7:00 AM</td><td>Wake up</td></tr><tr><td>1:00 – 2:00 PM</td><td>Quiet time in their room</td></tr><tr><td>6:45 – 7:30 PM</td><td>Bedtime (earlier than on nap days)</td></tr></tbody></table>'
        if a["key"] == "newborn":
            extra = "<p><em>Newborn days rarely look this tidy. Use this as a rough picture of how often your baby may sleep, not a schedule to enforce.</em></p>"
        body = f"""<h1>{esc(a['label'])} nap schedule</h1>
<p class="lead">{esc(a['desc'])}</p>
<table class="glance"><tbody>
<tr><td>Total sleep (24 hrs)</td><td>{a['total']}</td></tr>
<tr><td>Naps per day</td><td>{a['naps_count']}</td></tr>
<tr><td>Wake windows</td><td>{a['ww_range']}</td></tr>
<tr><td>Daytime sleep</td><td>{a['day_sleep']}</td></tr>
<tr><td>Typical bedtime</td><td>{a['bedtime']}</td></tr></tbody></table>
{a['intro']}
{ad_slot()}
<h2>Sample {esc(a['short'])} schedule</h2>
<p>Based on a 7:00 AM wake-up. Your times will shift with your baby's wake time. <a href="/nap-calculator/?age={a['key']}">Get times for your day →</a></p>
<table><thead><tr><th>Time</th><th>What happens</th></tr></thead><tbody>{rows}</tbody></table>
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
    grid = "".join(f'<li><a href="/schedules/{a["slug"]}/">{esc(a["label"])}<small>{a["naps_count"]} naps · wake windows {a["ww_range"]}</small></a></li>' for a in AGES)
    summary = "".join(f'<tr><td><a href="/schedules/{a["slug"]}/">{esc(a["label"])}</a></td><td>{a["naps_count"]}</td><td>{a["ww_range"]}</td><td>{a["total"]}</td></tr>' for a in AGES)
    body = f"""<h1>Nap schedules by age</h1>
<p class="lead">Pick your child's age for a typical nap schedule, wake windows, and a sample day, from newborn to 5 years.</p>
<ul class="grid">{grid}</ul>
<h2>Nap chart at a glance</h2>
<table><thead><tr><th>Age</th><th>Naps</th><th>Wake windows</th><th>Total sleep / 24h</th></tr></thead><tbody>{summary}</tbody></table>
<p>Total sleep ranges follow the American Academy of Sleep Medicine recommendations endorsed by the American Academy of Pediatrics (for babies 4 months and older) and the National Sleep Foundation (for newborns).</p>
{DISCLAIMER}"""
    pages.append(page("/schedules/", "Baby & Toddler Nap Schedules by Age (Newborn to 5 Years)",
                      "Nap schedules for every age from newborn to 5 years: how many naps, wake windows, total sleep, and sample days.",
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
                      f'<h1>Nap guides</h1><p class="lead">Short, practical guides for the trickiest parts of naps.</p><ul class="grid">{grid}</ul>',
                      crumbs=[H, ("Guides", "/guides/")]))

    # Calculator
    calc_data = {a["key"]: {"label": a["label"], "ww": a["ww"], "naps": a["naps"], "slug": a["slug"]} for a in AGES}
    opts = "".join(f'<option value="{a["key"]}">{esc(a["label"])}</option>' for a in AGES)
    calc_faq = [("How does the nap calculator work?", "It uses typical wake windows and nap lengths for your child's age, starting from the time they woke up, to estimate when each nap and bedtime should fall."),
                ("What if my baby's nap runs shorter or longer?", "Use the times as a starting point. If a nap is shorter than planned, the next nap usually comes a little earlier; if it's longer, a little later. Watch for sleepy cues.")]
    body = f"""<h1>Nap time calculator</h1>
<p class="lead">Enter your child's age and what time they woke up. We'll suggest nap times and a bedtime based on typical wake windows.</p>
<div class="card">
<label for="age">Child's age</label><select id="age">{opts}</select>
<label for="wake">Woke up at</label><input type="time" id="wake" value="07:00">
<p><button class="btn" id="go" type="button">Calculate schedule</button></p>
<div id="out" aria-live="polite"></div>
</div>
{INSTALL_HINT}
<script>
const D={json.dumps(calc_data)};
function f(m){{m=((m%1440)+1440)%1440;let h=Math.floor(m/60),mm=m%60,ap=h<12?'AM':'PM';h=h%12||12;return h+':'+String(mm).padStart(2,'0')+' '+ap}}
function d(m){{const h=Math.floor(m/60),x=m%60;return (h?h+' hr'+(h>1?'s':''):'')+(h&&x?' ':'')+(x?x+' min':'')}}
function run(){{const a=D[document.getElementById('age').value];const v=document.getElementById('wake').value||'07:00';let [h,m]=v.split(':').map(Number);let t=h*60+m;
let r='<table><thead><tr><th>Time</th><th>What happens</th></tr></thead><tbody><tr><td>'+f(t)+'</td><td>Wake up</td></tr>';
a.naps.forEach((n,i)=>{{t+=a.ww[i];r+='<tr><td>'+f(t)+' – '+f(t+n)+'</td><td>Nap '+(i+1)+' (about '+d(n)+')</td></tr>';t+=n}});
t+=a.ww[a.naps.length];r+='<tr><td>'+f(t)+'</td><td>Bedtime</td></tr></tbody></table>';
r+='<p>These are estimates. Watch your child for sleepy cues and adjust by 15 minutes or so. <a href="/schedules/'+a.slug+'/">See the full '+a.label+' guide →</a></p>';
document.getElementById('out').innerHTML=r}}
let q=new URLSearchParams(location.search).get('age');if(!q){{try{{q=localStorage.getItem('napAge')}}catch(e){{}}}}if(q&&D[q])document.getElementById('age').value=q;
document.getElementById('age').addEventListener('change',e=>{{try{{localStorage.setItem('napAge',e.target.value)}}catch(_){{}}}});
document.getElementById('go').addEventListener('click',run);document.getElementById('age').addEventListener('change',run);document.getElementById('wake').addEventListener('change',run);run();
</script>
{ad_slot()}
<h2>How to use these times</h2>
<p>The calculator assumes each nap lasts a typical length for your child's age. Real naps vary, so treat the result as a plan for the day, not a rule. If a nap ends early, the next one usually needs to start earlier. For newborns, follow your baby's hunger and sleepy cues first.</p>
<p>Learn more about <a href="/guides/wake-windows/">wake windows by age</a>.</p>
{faq_html(calc_faq)}
{DISCLAIMER}"""
    pages.append(page("/nap-calculator/", "Nap Time Calculator: Baby & Toddler Nap Schedule Maker",
                      "Free nap time calculator: enter your baby's age and wake-up time to get suggested nap times and bedtime, newborn to 5 years.",
                      body, schema=[faq_schema(calc_faq), {"@context": "https://schema.org", "@type": "WebApplication", "name": "Nap Time Calculator",
                                                          "url": SITE + "/nap-calculator/", "applicationCategory": "LifestyleApplication",
                                                          "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}],
                      crumbs=[H, ("Nap calculator", "/nap-calculator/")]))

    # Gear
    items = "".join(f'<div class="card gear"><h3>{esc(t)}</h3><p>{esc(p)}</p><a class="btn" href="{esc(amazon_url(q))}" rel="sponsored nofollow noopener" target="_blank">See options on Amazon</a></div>' for t, q, p in GEAR)
    body = f"""<h1>Nap gear that actually helps</h1>
<p class="lead">You don't need much to get good naps. These are the few things that make the biggest difference for most families.</p>
<p class="note">As an Amazon Associate we earn from qualifying purchases. It doesn't change the price you pay.</p>
{items}
<p>Whatever you buy, keep the crib bare: a firm mattress and fitted sheet only. See <a href="/guides/safe-sleep-basics/">safe sleep basics</a>.</p>"""
    pages.append(page("/nap-gear/", "Baby Nap Essentials: Gear That Helps Naps", "The few baby and toddler nap essentials that make the biggest difference: white noise, blackout shades, sleep sacks, and toddler clocks.",
                      body, crumbs=[H, ("Nap gear", "/nap-gear/")]))

    # Static info pages
    pages.append(page("/about/", "About NapSchedule", "About NapSchedule.com: simple, practical nap schedules for babies and toddlers.",
                      """<h1>About NapSchedule</h1><p>NapSchedule.com is a simple, no-nonsense reference for baby and toddler nap schedules. Our goal is to give tired parents clear, practical answers: how many naps, how long between them, and what a typical day looks like at each age.</p>
<p>Our schedules are based on widely used pediatric sleep guidance, including the total sleep recommendations from the American Academy of Sleep Medicine (endorsed by the American Academy of Pediatrics) and the AAP's safe sleep recommendations. Typical ranges are just that: typical. Your child may need a little more or less.</p>
<p>We keep the site free with advertising and affiliate links. See our <a href="/privacy/">privacy policy</a> and <a href="/disclaimer/">disclaimer</a>.</p>""" + DISCLAIMER))
    pages.append(page("/disclaimer/", "Disclaimer", "Medical and affiliate disclaimer for NapSchedule.com.",
                      """<h1>Disclaimer</h1><h2>Not medical advice</h2><p>The content on NapSchedule.com is for general informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always ask your pediatrician or another qualified health provider about your child's health and sleep. If you think your child may have a medical emergency, call your doctor or emergency services immediately.</p>
<h2>Affiliate disclosure</h2><p>NapSchedule.com is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com. As an Amazon Associate we earn from qualifying purchases. This doesn't change the price you pay.</p>"""))
    pages.append(page("/privacy/", "Privacy Policy", "Privacy policy for NapSchedule.com.",
                      f"""<h1>Privacy policy</h1><p>Last updated: {TODAY}</p>
<p>NapSchedule.com does not ask you to create an account and does not collect personal information through forms. The nap calculator runs entirely in your browser; the age and times you enter are not sent to us.</p>
<h2>Advertising</h2><p>We may use third-party advertising companies, such as Google AdSense, to serve ads. These companies may use cookies to serve ads based on your prior visits to this and other websites. Google's use of advertising cookies enables it and its partners to serve ads based on your visits to this site and/or other sites on the Internet. You may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" rel="noopener" target="_blank">Google Ads Settings</a>. Learn more at <a href="https://policies.google.com/technologies/partner-sites" rel="noopener" target="_blank">how Google uses information from sites that use its services</a>.</p>
<h2>Affiliate links</h2><p>Some links go to Amazon. If you buy through them, Amazon may use cookies to attribute the purchase to us. See the <a href="/disclaimer/">disclaimer</a>.</p>
<h2>Hosting</h2><p>This site is hosted on GitHub Pages, which may log basic technical information such as IP addresses for security purposes.</p>
<h2>Children</h2><p>This site is written for parents and caregivers and is not directed to children under 13.</p>"""))

    # Home
    grid = "".join(f'<li><a href="/schedules/{a["slug"]}/">{esc(a["label"])}<small>Naps: {a["naps_count"]}</small></a></li>' for a in AGES)
    ggrid = "".join(f'<li><a href="/guides/{g["slug"]}/">{esc(g["h1"])}</a></li>' for g in GUIDES)
    home_faq = [("How many naps does a baby need?", "It depends on age: newborns take 4–7 naps, 4–5 month olds take 3–4, 6–7 month olds take 3, babies from about 8 months to 15 months take 2, and most toddlers take 1 nap until somewhere between ages 3 and 5."),
                ("When do babies drop to one nap?", "Most toddlers move from two naps to one between 13 and 18 months."),
                ("What is a wake window?", "A wake window is the time a child is awake between sleeps. It grows from under an hour for newborns to 5–6 hours for toddlers.")]
    body = f"""<h1>Baby & toddler nap schedules, by age</h1>
<p class="lead">Simple nap schedules from newborn to 5 years: how many naps, how long between them, and what a typical day looks like. Plus a free calculator that builds a schedule from your child's wake-up time.</p>
<p><a class="btn" href="/nap-calculator/">Open the nap calculator</a></p>
<h2>Find your child's schedule</h2><ul class="grid">{grid}</ul>
{ad_slot()}
<h2>Popular guides</h2><ul class="grid">{ggrid}</ul>
{gear_box()}
{faq_html(home_faq)}
{DISCLAIMER}"""
    pages.append(page("/", "Nap Schedules by Age: Baby & Toddler Nap Schedule + Calculator",
                      "Free baby and toddler nap schedules by age, newborn to 5 years: wake windows, number of naps, sample days, and a nap time calculator.",
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
        "name": "Nap Time Calculator by NapSchedule", "short_name": "Nap Times",
        "description": "Nap times and bedtime for your baby or toddler, based on age and wake-up time.",
        "id": "/nap-calculator/", "start_url": "/nap-calculator/?source=pwa", "scope": "/",
        "display": "standalone", "background_color": "#fbf8f3", "theme_color": "#3d5a80",
        "icons": [
            {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [{"name": "Nap schedules by age", "url": "/schedules/"}],
    }
    with open(os.path.join(OUT, "manifest.webmanifest"), "w") as f:
        json.dump(manifest, f, indent=1)
    precache = ["/", "/nap-calculator/", "/schedules/", "/style.css", "/favicon.svg", "/manifest.webmanifest",
                "/icons/icon-192.png", "/icons/icon-512.png", "/icons/icon-180.png"] + [p for p in pages if p.startswith("/schedules/")]
    version = hashlib.sha1("".join(open(os.path.join(dp, fn), "rb").read().hex() for dp, _, fns in sorted(os.walk(OUT)) for fn in sorted(fns)).encode()).hexdigest()[:10]
    with open(os.path.join(OUT, "sw.js"), "w") as f:
        f.write(SW.replace("__VERSION__", version).replace("__PRECACHE__", json.dumps(sorted(set(precache)))))
    with open(os.path.join(OUT, "CNAME"), "w") as f:
        f.write("napschedule.com\n")
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
