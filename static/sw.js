// Dopamine.watch Service Worker v2
// Enhanced caching with local storage support
const CACHE_NAME = 'dopamine-v2';
const STATIC_CACHE = 'dopamine-static-v2';
const DYNAMIC_CACHE = 'dopamine-dynamic-v2';
const OFFLINE_URL = '/static/offline.html';

// Static assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/static/offline.html',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

// Cache strategies
const CACHE_STRATEGIES = {
    cacheFirst: ['icon', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'woff2', 'woff', 'ttf'],
    networkFirst: ['html', 'css', 'js'],
    staleWhileRevalidate: ['json']
};

// Install event - cache essential assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker v2...');
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE)
                .then((cache) => {
                    console.log('[SW] Caching static assets');
                    return cache.addAll(STATIC_ASSETS);
                }),
            // Skip waiting
            self.skipWaiting()
        ])
        .then(() => console.log('[SW] Install complete'))
        .catch((err) => console.log('[SW] Install failed:', err))
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker v2...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => {
                            return name.startsWith('dopamine-') &&
                                   name !== STATIC_CACHE &&
                                   name !== DYNAMIC_CACHE;
                        })
                        .map((name) => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Activation complete');
                return self.clients.claim();
            })
    );
});

// Helper: Get file extension
function getExtension(url) {
    const pathname = new URL(url).pathname;
    const parts = pathname.split('.');
    return parts.length > 1 ? parts.pop().toLowerCase() : '';
}

// Helper: Get cache strategy based on file type
function getCacheStrategy(url) {
    const ext = getExtension(url);

    if (CACHE_STRATEGIES.cacheFirst.includes(ext)) {
        return 'cacheFirst';
    }
    if (CACHE_STRATEGIES.networkFirst.includes(ext)) {
        return 'networkFirst';
    }
    if (CACHE_STRATEGIES.staleWhileRevalidate.includes(ext)) {
        return 'staleWhileRevalidate';
    }
    return 'networkFirst';
}

// Cache First Strategy (for images, fonts)
async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) {
        return cached;
    }

    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        return new Response('', { status: 503 });
    }
}

// Network First Strategy (for HTML, CSS, JS)
async function networkFirst(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        const cached = await caches.match(request);
        if (cached) {
            return cached;
        }

        // For navigation requests, return offline page
        if (request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
        }

        return new Response('', { status: 503 });
    }
}

// Stale While Revalidate Strategy (for JSON, API responses)
async function staleWhileRevalidate(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cached = await cache.match(request);

    // Fetch in background
    const fetchPromise = fetch(request)
        .then((response) => {
            if (response.ok) {
                cache.put(request, response.clone());
            }
            return response;
        })
        .catch(() => null);

    // Return cached if available, otherwise wait for network
    return cached || fetchPromise;
}

// Fetch event handler
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    const url = new URL(event.request.url);

    // Skip external requests, API calls, Supabase
    if (
        url.hostname !== self.location.hostname ||
        url.hostname.includes('supabase') ||
        url.hostname.includes('api.') ||
        url.pathname.includes('/api/') ||
        url.pathname.includes('/_stcore/') ||
        url.pathname.includes('/component/')
    ) {
        return;
    }

    const strategy = getCacheStrategy(event.request.url);

    switch (strategy) {
        case 'cacheFirst':
            event.respondWith(cacheFirst(event.request));
            break;
        case 'networkFirst':
            event.respondWith(networkFirst(event.request));
            break;
        case 'staleWhileRevalidate':
            event.respondWith(staleWhileRevalidate(event.request));
            break;
        default:
            event.respondWith(networkFirst(event.request));
    }
});

// Handle messages from the app
self.addEventListener('message', (event) => {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }

    // Store recent recommendations for offline access
    if (event.data.type === 'CACHE_RECOMMENDATIONS') {
        cacheRecommendations(event.data.recommendations);
    }

    // Clear specific cache
    if (event.data.type === 'CLEAR_CACHE') {
        caches.delete(event.data.cacheName || DYNAMIC_CACHE);
    }
});

// Cache recommendations for offline access
async function cacheRecommendations(recommendations) {
    if (!recommendations || !Array.isArray(recommendations)) return;

    // Store in IndexedDB for offline access
    const db = await openDB();
    const tx = db.transaction('recommendations', 'readwrite');
    const store = tx.objectStore('recommendations');

    // Clear old recommendations
    await store.clear();

    // Add new recommendations
    for (const rec of recommendations.slice(0, 20)) {
        await store.add({
            ...rec,
            cachedAt: Date.now()
        });
    }
}

// Open IndexedDB
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('DopamineDB', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            // Create recommendations store
            if (!db.objectStoreNames.contains('recommendations')) {
                db.createObjectStore('recommendations', { keyPath: 'id', autoIncrement: true });
            }

            // Create user preferences store
            if (!db.objectStoreNames.contains('preferences')) {
                db.createObjectStore('preferences', { keyPath: 'key' });
            }

            // Create mood history store
            if (!db.objectStoreNames.contains('moodHistory')) {
                const store = db.createObjectStore('moodHistory', { keyPath: 'id', autoIncrement: true });
                store.createIndex('timestamp', 'timestamp');
            }
        };
    });
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('[SW] Sync event:', event.tag);

    if (event.tag === 'sync-mood') {
        event.waitUntil(syncMoodHistory());
    }

    if (event.tag === 'sync-queue') {
        event.waitUntil(syncWatchQueue());
    }
});

// Sync mood history when back online
async function syncMoodHistory() {
    try {
        const db = await openDB();
        const tx = db.transaction('moodHistory', 'readonly');
        const store = tx.objectStore('moodHistory');
        const moods = await store.getAll();

        if (moods && moods.length > 0) {
            // Send to server
            await fetch('/api/sync-moods', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ moods })
            });

            // Clear synced data
            const clearTx = db.transaction('moodHistory', 'readwrite');
            await clearTx.objectStore('moodHistory').clear();
        }
    } catch (err) {
        console.log('[SW] Mood sync failed:', err);
    }
}

// Sync watch queue when back online
async function syncWatchQueue() {
    // Similar implementation for watch queue sync
    console.log('[SW] Syncing watch queue...');
}

// Push notification handler
self.addEventListener('push', (event) => {
    console.log('[SW] Push received');

    let data = { title: 'Dopamine.watch', body: 'Time for your dopamine fix!' };

    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/icon-192.png',
        vibrate: [100, 50, 100],
        data: {
            url: data.url || '/'
        },
        actions: [
            { action: 'open', title: 'Open App' },
            { action: 'close', title: 'Dismiss' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'close') return;

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Focus existing window if available
                for (const client of clientList) {
                    if (client.url === event.notification.data.url && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(event.notification.data.url);
                }
            })
    );
});

console.log('[SW] Service Worker v2 loaded');
