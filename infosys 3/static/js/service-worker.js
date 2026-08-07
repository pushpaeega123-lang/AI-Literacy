const CACHE_NAME = 'learning-assistant-cache-v1';
const OFFLINE_URL = '/offline';

const ASSETS_TO_CACHE = [
  OFFLINE_URL,
  '/',
  '/login',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/notifications.js',
  '/static/js/mascot.js',
  '/static/js/voice_eval.js',
  '/static/js/tracing.js',
  '/static/js/keyboard.js',
  '/static/images/logo.png',
  '/static/images/hero_illustration.png',
  '/static/images/icons/icon_192.png',
  '/static/images/icons/icon_512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
  'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Noto+Sans+Telugu&family=Noto+Sans+Devanagari:wght@400;700&display=swap'
];

// Install Event - Pre-cache offline page and critical assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Pre-caching offline assets');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate Event - Clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Cleaning old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - Handle caching strategies
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Avoid intercepting local dev web-sockets or browser extension requests
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  // If the request is for a navigation page (HTML document)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clone the response and add it to cache for offline access
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // If network fails, try fetching from cache
          return caches.match(event.request)
            .then(cachedResponse => {
              if (cachedResponse) {
                return cachedResponse;
              }
              // If not in cache, return the offline fallback page
              return caches.match(OFFLINE_URL);
            });
        })
    );
    return;
  }

  // Stale-While-Revalidate for CSS, JS, Fonts, and static images
  if (
    event.request.destination === 'style' ||
    event.request.destination === 'script' ||
    event.request.destination === 'font' ||
    event.request.destination === 'image' ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('cdn.jsdelivr.net')
  ) {
    event.respondWith(
      caches.match(event.request)
        .then(cachedResponse => {
          const fetchPromise = fetch(event.request).then(networkResponse => {
            if (networkResponse && networkResponse.status === 200) {
              const responseClone = networkResponse.clone();
              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, responseClone);
              });
            }
            return networkResponse;
          }).catch(err => {
            console.warn('[Service Worker] Fetch failed for static asset:', event.request.url);
          });

          // Return cached response if available, otherwise wait for network
          return cachedResponse || fetchPromise;
        })
    );
    return;
  }

  // Default Network-First cache fallback strategy for other static assets/API GETs
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        return cachedResponse || fetch(event.request).then(response => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          return response;
        }).catch(() => {
          // Ignore API requests that fail or other dynamic requests
        });
      })
  );
});

// Push Notification Event
self.addEventListener('push', event => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = {
        title: 'New Notification',
        body: event.data.text()
      };
    }
  }

  const title = data.title || 'Daily Learning Reminder 📚';
  const options = {
    body: data.body || "Let's continue learning together! Open the app to start.",
    icon: data.icon || '/static/images/icons/icon_192.png',
    badge: data.badge || '/static/images/icons/icon_72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification Click Event
self.addEventListener('notificationclick', event => {
  event.notification.close();
  const targetUrl = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      // If there's an existing window open, navigate/focus it
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus().then(() => client.navigate(targetUrl));
        }
      }
      // Otherwise open a new window
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});

// Background Sync Event
self.addEventListener('sync', event => {
  if (event.tag === 'sync-progress') {
    console.log('[Service Worker] Syncing user progress tag matches');
  }
});
