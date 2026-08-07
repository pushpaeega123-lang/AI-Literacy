// ======================================
// PWA Notifications Management
// notifications.js
// ======================================

const VAPID_KEY_URL = '/api/vapid-public-key';
const SUBSCRIBE_URL = '/api/notifications/subscribe';
const SETTINGS_URL = '/api/notifications/settings';
const TRIGGER_DEMO_URL = '/api/notifications/trigger-demo';

// Helper to convert base64 VAPID public key to Uint8Array for subscription
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Check current notification state and setup event listeners
document.addEventListener("DOMContentLoaded", function() {
    initNotificationUI();
});

function initNotificationUI() {
    const toggle = document.getElementById("notificationsToggle");
    const testBtn = document.getElementById("testNotificationBtn");

    if (toggle) {
        // Sync toggle state with browser permission
        if (Notification.permission === "granted" && toggle.dataset.enabled === "1") {
            toggle.checked = true;
        } else if (Notification.permission === "denied") {
            toggle.checked = false;
            toggle.disabled = true;
            const statusText = document.getElementById("notificationsStatusText");
            if (statusText) statusText.innerText = "Blocked by Browser";
        } else {
            toggle.checked = false;
        }

        toggle.addEventListener("change", function() {
            if (this.checked) {
                enableNotifications();
            } else {
                disableNotifications();
            }
        });
    }

    if (testBtn) {
        testBtn.addEventListener("click", function() {
            const select = document.getElementById("testNotificationType");
            const type = select ? select.value : "daily_learning";
            triggerDemoNotification(type);
        });
    }
}

// Request permission and subscribe
async function enableNotifications() {
    const toggle = document.getElementById("notificationsToggle");
    const statusText = document.getElementById("notificationsStatusText");

    try {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            alert("Push notifications are not supported in this browser.");
            if (toggle) toggle.checked = false;
            return;
        }

        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
            alert("Notification permission denied. Please enable them in your browser settings.");
            if (toggle) {
                toggle.checked = false;
                if (permission === "denied") toggle.disabled = true;
            }
            if (statusText) statusText.innerText = permission === "denied" ? "Blocked by Browser" : "Disabled";
            return;
        }

        if (statusText) statusText.innerText = "Enabling...";

        // Register subscription with push service
        const registration = await navigator.serviceWorker.ready;
        
        // Fetch VAPID public key
        const response = await fetch(VAPID_KEY_URL);
        const data = await response.json();
        const vapidPublicKey = data.publicKey;

        if (!vapidPublicKey || vapidPublicKey === "dummy-private-key" || vapidPublicKey.startsWith("BDH1oQ")) {
            console.warn("Using mock VAPID setup. Standard Web Push may fail; falling back to local client notifications.");
        }

        const subscribeOptions = {
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
        };

        const subscription = await registration.pushManager.subscribe(subscribeOptions);
        
        // Send subscription to backend
        await fetch(SUBSCRIBE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(subscription)
        });

        // Update settings in database
        await fetch(SETTINGS_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notifications_enabled: 1 })
        });

        if (statusText) statusText.innerText = "Enabled & Active";
        console.log("Successfully subscribed to Push Notifications.");

    } catch (error) {
        console.error("Failed to enable notifications:", error);
        alert("Error subscribing to notification service. Falling back to local notifications.");
        
        // Save database preference anyway so client-side fallback triggers can still work
        await fetch(SETTINGS_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notifications_enabled: 1 })
        }).catch(err => console.error(err));

        if (statusText) statusText.innerText = "Local Mode Active";
    }
}

// Unsubscribe
async function disableNotifications() {
    const toggle = document.getElementById("notificationsToggle");
    const statusText = document.getElementById("notificationsStatusText");

    try {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();
            if (subscription) {
                await subscription.unsubscribe();
                console.log("Unsubscribed from push service.");
            }
        }

        // Save settings in database
        await fetch(SETTINGS_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notifications_enabled: 0 })
        });

        if (statusText) statusText.innerText = "Disabled";
    } catch (error) {
        console.error("Error disabling notifications:", error);
        if (statusText) statusText.innerText = "Error disabling";
    }
}

// Trigger demo notifications (Daily learning, Achievement, etc.)
async function triggerDemoNotification(type) {
    console.log(`Triggering test notification of type: ${type}`);

    try {
        // First check permission
        if (Notification.permission !== "granted") {
            const permission = await Notification.requestPermission();
            if (permission !== "granted") {
                alert("Please enable notification permissions first.");
                return;
            }
        }

        // Trigger backend API
        const response = await fetch(TRIGGER_DEMO_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type })
        });

        const data = await response.json();

        if (data.status === "success") {
            console.log("Notification route triggered successfully. Web push sent status:", data.web_push_sent);
            
            // If backend standard Web Push was not sent or encountered an error,
            // or if we are testing locally without full secure HTTPS web push tunnels,
            // fall back to triggering a local browser notification using the Service Worker!
            if (!data.web_push_sent) {
                console.log("Falling back to local notification trigger via Service Worker registration...");
                if ('serviceWorker' in navigator) {
                    const registration = await navigator.serviceWorker.ready;
                    registration.showNotification(data.notification.title, {
                        body: data.notification.body,
                        icon: '/static/images/icons/icon_192.png',
                        badge: '/static/images/icons/icon_72.png',
                        data: {
                            url: data.notification.url
                        }
                    });
                } else {
                    // Fallback to basic window Notification
                    new Notification(data.notification.title, {
                        body: data.notification.body,
                        icon: '/static/images/icons/icon_192.png'
                    });
                }
            }
        } else {
            alert("Error: " + (data.message || "Failed to trigger. Make sure notifications are enabled in settings below."));
        }
    } catch (error) {
        console.error("Error triggering test notification:", error);
        alert("Failed to trigger demo notification. Check console for details.");
    }
}
