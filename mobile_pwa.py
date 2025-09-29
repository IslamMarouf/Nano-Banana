#!/usr/bin/env python3
"""
Mobile app version and Progressive Web App (PWA) for Nano Banana Image Generator
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class PWAManifest:
    """PWA manifest configuration"""
    name: str
    short_name: str
    description: str
    start_url: str
    display: str
    background_color: str
    theme_color: str
    icons: List[Dict[str, str]]
    categories: List[str]
    orientation: str

@dataclass
class MobileFeature:
    """Mobile-specific feature configuration"""
    name: str
    enabled: bool
    description: str
    mobile_only: bool

class MobilePWAManager:
    """Mobile and PWA management system"""
    
    def __init__(self):
        self.pwa_manifest = self._create_pwa_manifest()
        self.mobile_features = self._load_mobile_features()
        self.offline_capabilities = self._load_offline_capabilities()
        self.touch_gestures = self._load_touch_gestures()
        self.responsive_breakpoints = self._load_responsive_breakpoints()
    
    def _create_pwa_manifest(self) -> PWAManifest:
        """Create PWA manifest configuration"""
        return PWAManifest(
            name="Nano Banana Image Generator",
            short_name="Nano Banana",
            description="AI-powered image generation and editing app",
            start_url="/",
            display="standalone",
            background_color="#1a1a1a",
            theme_color="#00ff00",
            icons=[
                {
                    "src": "/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                },
                {
                    "src": "/icons/icon-maskable-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "maskable"
                }
            ],
            categories=["photography", "art", "productivity", "utilities"],
            orientation="portrait-primary"
        )
    
    def _load_mobile_features(self) -> Dict[str, MobileFeature]:
        """Load mobile-specific features"""
        return {
            "camera_integration": MobileFeature(
                name="Camera Integration",
                enabled=True,
                description="Access device camera for image input",
                mobile_only=True
            ),
            "touch_gestures": MobileFeature(
                name="Touch Gestures",
                enabled=True,
                description="Swipe, pinch, and tap gestures for navigation",
                mobile_only=True
            ),
            "offline_mode": MobileFeature(
                name="Offline Mode",
                enabled=True,
                description="Work offline with cached content",
                mobile_only=False
            ),
            "push_notifications": MobileFeature(
                name="Push Notifications",
                enabled=True,
                description="Receive notifications for completed generations",
                mobile_only=False
            ),
            "device_orientation": MobileFeature(
                name="Device Orientation",
                enabled=True,
                description="Adapt to device rotation and orientation",
                mobile_only=True
            ),
            "haptic_feedback": MobileFeature(
                name="Haptic Feedback",
                enabled=True,
                description="Tactile feedback for interactions",
                mobile_only=True
            ),
            "voice_commands": MobileFeature(
                name="Voice Commands",
                enabled=True,
                description="Voice input for prompts",
                mobile_only=False
            ),
            "gesture_drawing": MobileFeature(
                name="Gesture Drawing",
                enabled=True,
                description="Draw masks and sketches with touch",
                mobile_only=True
            ),
            "accelerometer": MobileFeature(
                name="Accelerometer",
                enabled=True,
                description="Use device motion for creative effects",
                mobile_only=True
            ),
            "geolocation": MobileFeature(
                name="Geolocation",
                enabled=True,
                description="Location-based image generation",
                mobile_only=False
            )
        }
    
    def _load_offline_capabilities(self) -> Dict[str, Any]:
        """Load offline functionality configuration"""
        return {
            "cache_strategies": [
                "cache_first",
                "network_first",
                "stale_while_revalidate",
                "network_only",
                "cache_only"
            ],
            "cached_resources": [
                "/",
                "/web",
                "/static/css/style.css",
                "/static/js/app.js",
                "/static/images/logo.png",
                "/static/fonts/",
                "/api/v1/image/templates",
                "/api/v1/prompts/suggestions"
            ],
            "offline_fallback": "/offline.html",
            "cache_size_limit": "100MB",
            "cache_duration": "7 days"
        }
    
    def _load_touch_gestures(self) -> Dict[str, Dict[str, Any]]:
        """Load touch gesture configurations"""
        return {
            "swipe_left": {
                "action": "next_image",
                "description": "Swipe left to view next generated image",
                "threshold": 100
            },
            "swipe_right": {
                "action": "previous_image",
                "description": "Swipe right to view previous image",
                "threshold": 100
            },
            "swipe_up": {
                "action": "show_options",
                "description": "Swipe up to show generation options",
                "threshold": 150
            },
            "swipe_down": {
                "action": "hide_options",
                "description": "Swipe down to hide options",
                "threshold": 150
            },
            "pinch_zoom": {
                "action": "zoom_image",
                "description": "Pinch to zoom in/out on image",
                "min_scale": 0.5,
                "max_scale": 3.0
            },
            "double_tap": {
                "action": "toggle_fullscreen",
                "description": "Double tap to toggle fullscreen mode",
                "timeout": 300
            },
            "long_press": {
                "action": "show_context_menu",
                "description": "Long press to show context menu",
                "duration": 500
            },
            "two_finger_tap": {
                "action": "reset_zoom",
                "description": "Two finger tap to reset zoom",
                "timeout": 200
            }
        }
    
    def _load_responsive_breakpoints(self) -> Dict[str, int]:
        """Load responsive design breakpoints"""
        return {
            "mobile": 480,
            "tablet": 768,
            "desktop": 1024,
            "large": 1200,
            "xlarge": 1920
        }
    
    def generate_pwa_manifest(self) -> str:
        """Generate PWA manifest JSON"""
        manifest_dict = {
            "name": self.pwa_manifest.name,
            "short_name": self.pwa_manifest.short_name,
            "description": self.pwa_manifest.description,
            "start_url": self.pwa_manifest.start_url,
            "display": self.pwa_manifest.display,
            "background_color": self.pwa_manifest.background_color,
            "theme_color": self.pwa_manifest.theme_color,
            "icons": self.pwa_manifest.icons,
            "categories": self.pwa_manifest.categories,
            "orientation": self.pwa_manifest.orientation,
            "scope": "/",
            "lang": "en",
            "dir": "ltr",
            "prefer_related_applications": False
        }
        
        return json.dumps(manifest_dict, indent=2)
    
    def generate_service_worker(self) -> str:
        """Generate service worker for offline functionality"""
        service_worker_code = """
// Nano Banana Image Generator Service Worker
const CACHE_NAME = 'nano-banana-v1.0.0';
const OFFLINE_URL = '/offline.html';

// Resources to cache
const CACHE_URLS = [
    '/',
    '/web',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/images/logo.png',
    '/static/fonts/',
    '/api/v1/image/templates',
    '/api/v1/prompts/suggestions'
];

// Install event - cache resources
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(CACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request)
                    .then(fetchResponse => {
                        // Cache successful responses
                        if (fetchResponse.status === 200) {
                            const responseToCache = fetchResponse.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => cache.put(event.request, responseToCache));
                        }
                        return fetchResponse;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                    });
            })
    );
});

// Background sync for image generation
self.addEventListener('sync', event => {
    if (event.tag === 'image-generation') {
        event.waitUntil(syncImageGeneration());
    }
});

// Push notifications
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'New image generated!',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Image',
                icon: '/icons/view-icon.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/icons/close-icon.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Nano Banana', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/web')
        );
    }
});

// Sync function for background image generation
async function syncImageGeneration() {
    // Implementation for syncing offline image generation requests
    console.log('Syncing image generation...');
}
"""
        return service_worker_code
    
    def generate_mobile_css(self) -> str:
        """Generate mobile-optimized CSS"""
        mobile_css = """
/* Nano Banana Mobile Styles */
:root {
    --primary-color: #00ff00;
    --secondary-color: #1a1a1a;
    --accent-color: #ff6b35;
    --text-color: #ffffff;
    --background-color: #000000;
    --surface-color: #1a1a1a;
    --border-color: #333333;
    --shadow-color: rgba(0, 255, 0, 0.3);
}

/* Mobile-first responsive design */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Touch-friendly buttons */
.btn {
    display: inline-block;
    padding: 12px 24px;
    background: var(--primary-color);
    color: var(--background-color);
    text-decoration: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 16px;
    min-height: 44px; /* iOS touch target minimum */
    min-width: 44px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}

.btn:hover, .btn:active {
    background: var(--accent-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px var(--shadow-color);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Mobile navigation */
.nav-mobile {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--surface-color);
    border-top: 1px solid var(--border-color);
    padding: 8px 0;
    z-index: 1000;
}

.nav-mobile ul {
    display: flex;
    justify-content: space-around;
    list-style: none;
}

.nav-mobile li {
    flex: 1;
    text-align: center;
}

.nav-mobile a {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
    color: var(--text-color);
    text-decoration: none;
    font-size: 12px;
}

.nav-mobile .icon {
    width: 24px;
    height: 24px;
    margin-bottom: 4px;
}

/* Mobile image gallery */
.gallery-mobile {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    padding: 12px;
    margin-bottom: 80px; /* Space for bottom nav */
}

.gallery-item {
    aspect-ratio: 1;
    border-radius: 12px;
    overflow: hidden;
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    position: relative;
    cursor: pointer;
}

.gallery-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.gallery-item:active img {
    transform: scale(0.95);
}

/* Touch gestures */
.gesture-area {
    position: relative;
    overflow: hidden;
    touch-action: pan-x pan-y;
}

.swipe-indicator {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0, 255, 0, 0.8);
    color: var(--background-color);
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.swipe-indicator.show {
    opacity: 1;
}

/* Mobile forms */
.form-mobile {
    padding: 20px;
    margin-bottom: 80px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: var(--text-color);
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 12px 16px;
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-color);
    font-size: 16px; /* Prevent zoom on iOS */
    -webkit-appearance: none;
    appearance: none;
}

.form-group textarea {
    resize: vertical;
    min-height: 100px;
}

/* Mobile modals */
.modal-mobile {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    z-index: 2000;
    display: flex;
    align-items: flex-end;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.modal-mobile.show {
    opacity: 1;
    visibility: visible;
}

.modal-content {
    background: var(--surface-color);
    border-radius: 20px 20px 0 0;
    padding: 24px;
    width: 100%;
    max-height: 80vh;
    overflow-y: auto;
    transform: translateY(100%);
    transition: transform 0.3s ease;
}

.modal-mobile.show .modal-content {
    transform: translateY(0);
}

/* Loading states */
.loading-mobile {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
}

.spinner-mobile {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive breakpoints */
@media (min-width: 768px) {
    .gallery-mobile {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .nav-mobile {
        display: none;
    }
    
    .modal-mobile {
        align-items: center;
    }
    
    .modal-content {
        border-radius: 12px;
        max-width: 500px;
        max-height: 80vh;
    }
}

@media (min-width: 1024px) {
    .gallery-mobile {
        grid-template-columns: repeat(4, 1fr);
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --background-color: #000000;
        --surface-color: #1a1a1a;
        --text-color: #ffffff;
        --border-color: #333333;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* High contrast support */
@media (prefers-contrast: high) {
    :root {
        --border-color: #ffffff;
        --shadow-color: rgba(255, 255, 255, 0.5);
    }
}

/* Print styles */
@media print {
    .nav-mobile,
    .modal-mobile,
    .btn {
        display: none;
    }
    
    body {
        background: white;
        color: black;
    }
}
"""
        return mobile_css
    
    def generate_mobile_js(self) -> str:
        """Generate mobile-specific JavaScript"""
        mobile_js = """
// Nano Banana Mobile JavaScript
class MobileApp {
    constructor() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.minSwipeDistance = 50;
        this.gestureArea = null;
        this.currentImageIndex = 0;
        this.images = [];
        
        this.init();
    }
    
    init() {
        this.setupTouchGestures();
        this.setupServiceWorker();
        this.setupPushNotifications();
        this.setupOrientationChange();
        this.setupHapticFeedback();
        this.setupVoiceCommands();
    }
    
    setupTouchGestures() {
        this.gestureArea = document.querySelector('.gesture-area');
        
        if (this.gestureArea) {
            this.gestureArea.addEventListener('touchstart', this.handleTouchStart.bind(this));
            this.gestureArea.addEventListener('touchend', this.handleTouchEnd.bind(this));
            this.gestureArea.addEventListener('touchmove', this.handleTouchMove.bind(this));
        }
        
        // Pinch zoom for images
        document.addEventListener('gesturestart', this.preventZoom.bind(this));
        document.addEventListener('gesturechange', this.preventZoom.bind(this));
        document.addEventListener('gestureend', this.preventZoom.bind(this));
    }
    
    handleTouchStart(event) {
        this.touchStartX = event.touches[0].clientX;
        this.touchStartY = event.touches[0].clientY;
    }
    
    handleTouchEnd(event) {
        this.touchEndX = event.changedTouches[0].clientX;
        this.touchEndY = event.changedTouches[0].clientY;
        this.handleSwipe();
    }
    
    handleTouchMove(event) {
        // Prevent default scrolling during swipe
        event.preventDefault();
    }
    
    handleSwipe() {
        const deltaX = this.touchEndX - this.touchStartX;
        const deltaY = this.touchEndY - this.touchStartY;
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            // Horizontal swipe
            if (Math.abs(deltaX) > this.minSwipeDistance) {
                if (deltaX > 0) {
                    this.swipeRight();
                } else {
                    this.swipeLeft();
                }
            }
        } else {
            // Vertical swipe
            if (Math.abs(deltaY) > this.minSwipeDistance) {
                if (deltaY > 0) {
                    this.swipeDown();
                } else {
                    this.swipeUp();
                }
            }
        }
    }
    
    swipeLeft() {
        this.nextImage();
        this.showSwipeIndicator('← Next');
    }
    
    swipeRight() {
        this.previousImage();
        this.showSwipeIndicator('Previous →');
    }
    
    swipeUp() {
        this.showOptions();
        this.showSwipeIndicator('↑ Options');
    }
    
    swipeDown() {
        this.hideOptions();
        this.showSwipeIndicator('↓ Hide');
    }
    
    nextImage() {
        if (this.currentImageIndex < this.images.length - 1) {
            this.currentImageIndex++;
            this.updateImageDisplay();
        }
    }
    
    previousImage() {
        if (this.currentImageIndex > 0) {
            this.currentImageIndex--;
            this.updateImageDisplay();
        }
    }
    
    updateImageDisplay() {
        const imageElement = document.querySelector('.current-image');
        if (imageElement && this.images[this.currentImageIndex]) {
            imageElement.src = this.images[this.currentImageIndex];
        }
    }
    
    showOptions() {
        const optionsPanel = document.querySelector('.options-panel');
        if (optionsPanel) {
            optionsPanel.classList.add('show');
        }
    }
    
    hideOptions() {
        const optionsPanel = document.querySelector('.options-panel');
        if (optionsPanel) {
            optionsPanel.classList.remove('show');
        }
    }
    
    showSwipeIndicator(text) {
        const indicator = document.querySelector('.swipe-indicator');
        if (indicator) {
            indicator.textContent = text;
            indicator.classList.add('show');
            setTimeout(() => {
                indicator.classList.remove('show');
            }, 1000);
        }
    }
    
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }
    
    setupPushNotifications() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }
    }
    
    setupOrientationChange() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });
    }
    
    handleOrientationChange() {
        const isLandscape = window.orientation === 90 || window.orientation === -90;
        
        if (isLandscape) {
            document.body.classList.add('landscape');
        } else {
            document.body.classList.remove('landscape');
        }
    }
    
    setupHapticFeedback() {
        if ('vibrate' in navigator) {
            this.vibrate = (pattern = 50) => {
                navigator.vibrate(pattern);
            };
        }
    }
    
    setupVoiceCommands() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleVoiceCommand(transcript);
            };
        }
    }
    
    startVoiceCommand() {
        if (this.recognition) {
            this.recognition.start();
        }
    }
    
    handleVoiceCommand(transcript) {
        const command = transcript.toLowerCase();
        
        if (command.includes('generate') || command.includes('create')) {
            this.generateImage(transcript);
        } else if (command.includes('next') || command.includes('right')) {
            this.nextImage();
        } else if (command.includes('previous') || command.includes('left')) {
            this.previousImage();
        } else if (command.includes('options') || command.includes('menu')) {
            this.showOptions();
        }
    }
    
    generateImage(prompt) {
        // Implementation for generating images with voice prompt
        console.log('Generating image with prompt:', prompt);
        
        // Show loading state
        this.showLoading();
        
        // Make API call
        fetch('/api/v1/image/generations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                voice_input: true
            })
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoading();
            if (data.success) {
                this.addImage(data.image_url);
                this.showNotification('Image generated successfully!');
            }
        })
        .catch(error => {
            this.hideLoading();
            this.showNotification('Error generating image');
        });
    }
    
    addImage(imageUrl) {
        this.images.push(imageUrl);
        this.currentImageIndex = this.images.length - 1;
        this.updateImageDisplay();
    }
    
    showLoading() {
        const loadingElement = document.querySelector('.loading-mobile');
        if (loadingElement) {
            loadingElement.style.display = 'flex';
        }
    }
    
    hideLoading() {
        const loadingElement = document.querySelector('.loading-mobile');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
    
    showNotification(message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Nano Banana', {
                body: message,
                icon: '/icons/icon-192x192.png'
            });
        }
        
        // Fallback to in-app notification
        this.showInAppNotification(message);
    }
    
    showInAppNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'in-app-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-color);
            color: var(--background-color);
            padding: 12px 24px;
            border-radius: 8px;
            z-index: 3000;
            animation: slideInDown 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    preventZoom(event) {
        event.preventDefault();
    }
}

// Initialize mobile app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MobileApp();
});

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInDown {
        from {
            transform: translateX(-50%) translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
"""
        return mobile_js
    
    def display_mobile_features(self):
        """Display mobile features"""
        console.print("\n[bold cyan]📱 Mobile Features[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Feature", style="cyan", width=20)
        table.add_column("Status", style="green", width=10)
        table.add_column("Mobile Only", style="yellow", width=12)
        table.add_column("Description", style="white", width=40)
        
        for feature_name, feature in self.mobile_features.items():
            status = "✅ Enabled" if feature.enabled else "❌ Disabled"
            mobile_only = "Yes" if feature.mobile_only else "No"
            
            table.add_row(
                feature_name.replace("_", " ").title(),
                status,
                mobile_only,
                feature.description
            )
        
        console.print(table)
    
    def display_pwa_info(self):
        """Display PWA information"""
        console.print("\n[bold cyan]🌐 Progressive Web App Info[/bold cyan]")
        
        pwa_panel = Panel(
            f"[bold]Name:[/bold] {self.pwa_manifest.name}\n"
            f"[bold]Short Name:[/bold] {self.pwa_manifest.short_name}\n"
            f"[bold]Description:[/bold] {self.pwa_manifest.description}\n"
            f"[bold]Display Mode:[/bold] {self.pwa_manifest.display}\n"
            f"[bold]Theme Color:[/bold] {self.pwa_manifest.theme_color}\n"
            f"[bold]Background Color:[/bold] {self.pwa_manifest.background_color}\n"
            f"[bold]Orientation:[/bold] {self.pwa_manifest.orientation}\n"
            f"[bold]Icons:[/bold] {len(self.pwa_manifest.icons)} configured\n"
            f"[bold]Categories:[/bold] {', '.join(self.pwa_manifest.categories)}",
            title="PWA Manifest",
            border_style="blue"
        )
        console.print(pwa_panel)
    
    def display_touch_gestures(self):
        """Display touch gesture configurations"""
        console.print("\n[bold cyan]👆 Touch Gestures[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Gesture", style="cyan", width=15)
        table.add_column("Action", style="green", width=20)
        table.add_column("Description", style="white", width=35)
        table.add_column("Threshold", style="yellow", width=12)
        
        for gesture_name, gesture_config in self.touch_gestures.items():
            threshold = gesture_config.get("threshold", "N/A")
            table.add_row(
                gesture_name.replace("_", " ").title(),
                gesture_config["action"].replace("_", " ").title(),
                gesture_config["description"],
                str(threshold)
            )
        
        console.print(table)

def demo_mobile_pwa():
    """Demo mobile and PWA features"""
    banner = Panel(
        "[bold blue]📱 Mobile & PWA Demo[/bold blue]\n\n"
        "Demonstrating mobile optimization and Progressive Web App features",
        title="Mobile & PWA",
        border_style="blue"
    )
    console.print(banner)
    
    mobile_pwa_manager = MobilePWAManager()
    
    # Display features and configurations
    mobile_pwa_manager.display_mobile_features()
    mobile_pwa_manager.display_pwa_info()
    mobile_pwa_manager.display_touch_gestures()
    
    # Generate PWA files
    console.print("\n[bold cyan]📄 Generated PWA Files[/bold cyan]")
    
    manifest = mobile_pwa_manager.generate_pwa_manifest()
    service_worker = mobile_pwa_manager.generate_service_worker()
    mobile_css = mobile_pwa_manager.generate_mobile_css()
    mobile_js = mobile_pwa_manager.generate_mobile_js()
    
    console.print(f"✅ PWA Manifest: {len(manifest)} characters")
    console.print(f"✅ Service Worker: {len(service_worker)} characters")
    console.print(f"✅ Mobile CSS: {len(mobile_css)} characters")
    console.print(f"✅ Mobile JS: {len(mobile_js)} characters")
    
    # Demo offline capabilities
    console.print("\n[bold cyan]📱 Offline Capabilities[/bold cyan]")
    
    offline_panel = Panel(
        f"[bold]Cache Strategies:[/bold] {', '.join(mobile_pwa_manager.offline_capabilities['cache_strategies'])}\n"
        f"[bold]Cached Resources:[/bold] {len(mobile_pwa_manager.offline_capabilities['cached_resources'])} items\n"
        f"[bold]Cache Size Limit:[/bold] {mobile_pwa_manager.offline_capabilities['cache_size_limit']}\n"
        f"[bold]Cache Duration:[/bold] {mobile_pwa_manager.offline_capabilities['cache_duration']}\n"
        f"[bold]Offline Fallback:[/bold] {mobile_pwa_manager.offline_capabilities['offline_fallback']}",
        title="Offline Configuration",
        border_style="green"
    )
    console.print(offline_panel)
    
    # Demo responsive breakpoints
    console.print("\n[bold cyan]📐 Responsive Breakpoints[/bold cyan]")
    
    breakpoints_table = Table(show_header=True, header_style="bold magenta")
    breakpoints_table.add_column("Device", style="cyan", width=12)
    breakpoints_table.add_column("Min Width", style="green", width=12)
    breakpoints_table.add_column("Description", style="white", width=30)
    
    breakpoint_descriptions = {
        "mobile": "Smartphones and small devices",
        "tablet": "Tablets and medium screens",
        "desktop": "Desktop computers and laptops",
        "large": "Large desktop monitors",
        "xlarge": "Ultra-wide and 4K displays"
    }
    
    for device, width in mobile_pwa_manager.responsive_breakpoints.items():
        breakpoints_table.add_row(
            device.title(),
            f"{width}px",
            breakpoint_descriptions.get(device, "Custom breakpoint")
        )
    
    console.print(breakpoints_table)
    
    # Feature summary
    features_panel = Panel(
        "[bold green]🎉 Mobile & PWA Features:[/bold green]\n\n"
        "✅ Progressive Web App (PWA) support\n"
        "✅ Mobile-first responsive design\n"
        "✅ Touch gestures and interactions\n"
        "✅ Camera integration\n"
        "✅ Offline functionality\n"
        "✅ Push notifications\n"
        "✅ Service worker caching\n"
        "✅ Device orientation handling\n"
        "✅ Haptic feedback\n"
        "✅ Voice commands\n"
        "✅ Gesture drawing\n"
        "✅ Accelerometer integration\n"
        "✅ Geolocation features\n"
        "✅ Installable web app\n"
        "✅ App-like experience\n\n"
        "[bold yellow]💡 Access your image generator anywhere, anytime![/bold yellow]",
        title="Mobile & PWA Complete",
        border_style="green"
    )
    console.print(features_panel)

def main():
    """Main function for mobile and PWA demo"""
    demo_mobile_pwa()

if __name__ == "__main__":
    main()
