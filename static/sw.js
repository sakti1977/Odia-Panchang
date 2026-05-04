// Odia Panchang — Basic Service Worker
// Caches static assets for faster loads on repeat visits.

const CACHE_NAME = 'odia-panchang-v1';
const STATIC_ASSETS = [
    '/',
    '/static/style.css',
    '/static/script.js',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Network-first for API calls (always fresh data)
    if (url.pathname.startsWith('/api') ||
        url.pathname.startsWith('/today') ||
        url.pathname.startsWith('/panchang') ||
        url.pathname.startsWith('/festivals') ||
        url.pathname.startsWith('/tweet')) {
        event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
        return;
    }

    // Cache-first for static assets
    event.respondWith(
        caches.match(event.request).then(cached => cached || fetch(event.request))
    );
});
