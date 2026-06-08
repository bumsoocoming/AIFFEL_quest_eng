// HERO 서비스 워커 — 설치 가능하게 하되, 항상 최신 내용 사용(network-first)
const CACHE = 'hero-v20';

self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });

self.addEventListener('fetch', e => {
  // 네트워크 우선 — 항상 최신. 오프라인일 때만 캐시 사용
  e.respondWith(
    fetch(e.request)
      .then(res => {
        // 성공 응답은 캐시에 저장(오프라인 대비)
        const copy = res.clone();
        caches.open(CACHE).then(c => { try { c.put(e.request, copy); } catch (err) {} });
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
