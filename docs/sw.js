// Offline support: same-origin only, so ad and affiliate requests are never cached.
const CACHE = 'nap-27d88ab999';
const PRECACHE = ["/", "/babywise/", "/babywise/babywise-schedule-6-9-months/", "/babywise/babywise-schedule-9-12-months/", "/babywise/babywise-schedule-weeks-1-2/", "/babywise/babywise-schedule-weeks-13-15/", "/babywise/babywise-schedule-weeks-16-24/", "/babywise/babywise-schedule-weeks-3-5/", "/babywise/babywise-schedule-weeks-6-7/", "/babywise/babywise-schedule-weeks-8-12/", "/favicon.svg", "/icons/icon-180.png", "/icons/icon-192.png", "/icons/icon-512.png", "/manifest.webmanifest", "/nap-calculator/", "/schedules/", "/schedules/11-14-month-nap-schedule/", "/schedules/15-18-month-nap-schedule/", "/schedules/19-24-month-nap-schedule/", "/schedules/2-3-year-old-nap-schedule/", "/schedules/3-5-year-old-nap-schedule/", "/style.css"];
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
