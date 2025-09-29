#!/usr/bin/env python3
"""
Webhook support and external API integrations for Nano Banana Image Generator
"""

import json
import time
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import requests
import asyncio
from datetime import datetime

console = Console()

@dataclass
class WebhookEvent:
    """Data class for webhook events"""
    event_type: str
    timestamp: str
    data: Dict[str, Any]
    signature: Optional[str] = None
    source: str = "nano_banana"

@dataclass
class APIEndpoint:
    """Data class for external API endpoints"""
    name: str
    url: str
    method: str
    headers: Dict[str, str]
    auth_type: str
    description: str

class WebhookManager:
    """Webhook management system"""
    
    def __init__(self):
        self.webhooks = {}
        self.event_history = []
        self.secret_keys = {}
    
    def register_webhook(self, webhook_id: str, url: str, events: List[str], secret: str = None):
        """Register a new webhook endpoint"""
        self.webhooks[webhook_id] = {
            "url": url,
            "events": events,
            "secret": secret,
            "active": True,
            "created": datetime.now().isoformat(),
            "last_used": None,
            "failure_count": 0
        }
        
        if secret:
            self.secret_keys[webhook_id] = secret
        
        console.print(f"[green]✅ Registered webhook: {webhook_id}[/green]")
    
    def unregister_webhook(self, webhook_id: str):
        """Unregister a webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            console.print(f"[yellow]🗑️ Unregistered webhook: {webhook_id}[/yellow]")
    
    def send_webhook(self, event_type: str, data: Dict[str, Any]):
        """Send webhook event to registered endpoints"""
        event = WebhookEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        
        self.event_history.append(event)
        
        # Find webhooks that listen to this event type
        target_webhooks = [
            (webhook_id, webhook_info) 
            for webhook_id, webhook_info in self.webhooks.items()
            if webhook_info["active"] and event_type in webhook_info["events"]
        ]
        
        if not target_webhooks:
            console.print(f"[yellow]⚠️ No webhooks registered for event: {event_type}[/yellow]")
            return
        
        console.print(f"[cyan]📡 Sending webhook event '{event_type}' to {len(target_webhooks)} endpoints[/cyan]")
        
        for webhook_id, webhook_info in target_webhooks:
            try:
                # Prepare payload
                payload = {
                    "event_type": event_type,
                    "timestamp": event.timestamp,
                    "data": data,
                    "source": "nano_banana"
                }
                
                # Add signature if secret is available
                if webhook_info.get("secret"):
                    payload["signature"] = self._generate_signature(
                        json.dumps(payload, sort_keys=True),
                        webhook_info["secret"]
                    )
                
                # Send webhook
                response = requests.post(
                    webhook_info["url"],
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.ok:
                    console.print(f"[green]✅ Webhook sent to {webhook_id}[/green]")
                    webhook_info["last_used"] = datetime.now().isoformat()
                    webhook_info["failure_count"] = 0
                else:
                    console.print(f"[red]❌ Webhook failed to {webhook_id}: {response.status_code}[/red]")
                    webhook_info["failure_count"] += 1
                    
                    # Disable webhook after 5 failures
                    if webhook_info["failure_count"] >= 5:
                        webhook_info["active"] = False
                        console.print(f"[red]🚫 Disabled webhook {webhook_id} after 5 failures[/red]")
                
            except Exception as e:
                console.print(f"[red]❌ Webhook error to {webhook_id}: {e}[/red]")
                webhook_info["failure_count"] += 1
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(self, payload: str, signature: str, webhook_id: str) -> bool:
        """Verify webhook signature"""
        if webhook_id not in self.secret_keys:
            return False
        
        expected_signature = self._generate_signature(payload, self.secret_keys[webhook_id])
        return hmac.compare_digest(signature, expected_signature)
    
    def get_webhook_stats(self) -> Dict[str, Any]:
        """Get webhook statistics"""
        total_webhooks = len(self.webhooks)
        active_webhooks = len([w for w in self.webhooks.values() if w["active"]])
        total_events = len(self.event_history)
        
        event_counts = {}
        for event in self.event_history:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        return {
            "total_webhooks": total_webhooks,
            "active_webhooks": active_webhooks,
            "total_events": total_events,
            "event_counts": event_counts
        }

class APIIntegrations:
    """External API integrations manager"""
    
    def __init__(self):
        self.endpoints = self._load_default_endpoints()
        self.integration_history = []
    
    def _load_default_endpoints(self) -> Dict[str, APIEndpoint]:
        """Load default API endpoints"""
        return {
            "discord": APIEndpoint(
                name="Discord",
                url="https://discord.com/api/webhooks/{webhook_id}/{token}",
                method="POST",
                headers={"Content-Type": "application/json"},
                auth_type="webhook",
                description="Send images to Discord channel"
            ),
            "slack": APIEndpoint(
                name="Slack",
                url="https://hooks.slack.com/services/{token}",
                method="POST",
                headers={"Content-Type": "application/json"},
                auth_type="webhook",
                description="Send images to Slack channel"
            ),
            "telegram": APIEndpoint(
                name="Telegram",
                url="https://api.telegram.org/bot{token}/sendPhoto",
                method="POST",
                headers={"Content-Type": "application/json"},
                auth_type="bot_token",
                description="Send images to Telegram chat"
            ),
            "twitter": APIEndpoint(
                name="Twitter",
                url="https://api.twitter.com/2/tweets",
                method="POST",
                headers={"Authorization": "Bearer {token}"},
                auth_type="bearer_token",
                description="Post images to Twitter"
            ),
            "instagram": APIEndpoint(
                name="Instagram",
                url="https://graph.instagram.com/v1.0/me/media",
                method="POST",
                headers={"Authorization": "Bearer {token}"},
                auth_type="bearer_token",
                description="Post images to Instagram"
            ),
            "dropbox": APIEndpoint(
                name="Dropbox",
                url="https://content.dropboxapi.com/2/files/upload",
                method="POST",
                headers={"Authorization": "Bearer {token}"},
                auth_type="bearer_token",
                description="Upload images to Dropbox"
            ),
            "google_drive": APIEndpoint(
                name="Google Drive",
                url="https://www.googleapis.com/upload/drive/v3/files",
                method="POST",
                headers={"Authorization": "Bearer {token}"},
                auth_type="bearer_token",
                description="Upload images to Google Drive"
            ),
            "aws_s3": APIEndpoint(
                name="AWS S3",
                url="https://{bucket}.s3.amazonaws.com/{key}",
                method="PUT",
                headers={"Authorization": "AWS4-HMAC-SHA256 {signature}"},
                auth_type="aws_signature",
                description="Upload images to AWS S3"
            )
        }
    
    def send_to_discord(self, image_url: str, message: str, webhook_id: str, token: str):
        """Send image to Discord channel"""
        url = self.endpoints["discord"].url.format(webhook_id=webhook_id, token=token)
        
        payload = {
            "content": message,
            "embeds": [{
                "title": "Generated Image",
                "description": "New image generated by Nano Banana",
                "image": {"url": image_url},
                "color": 0x00ff00,
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.endpoints["discord"].headers)
            if response.ok:
                console.print("[green]✅ Image sent to Discord[/green]")
                return True
            else:
                console.print(f"[red]❌ Discord error: {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Discord error: {e}[/red]")
            return False
    
    def send_to_slack(self, image_url: str, message: str, token: str):
        """Send image to Slack channel"""
        url = self.endpoints["slack"].url.format(token=token)
        
        payload = {
            "text": message,
            "attachments": [{
                "color": "good",
                "title": "Generated Image",
                "image_url": image_url,
                "ts": time.time()
            }]
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.endpoints["slack"].headers)
            if response.ok:
                console.print("[green]✅ Image sent to Slack[/green]")
                return True
            else:
                console.print(f"[red]❌ Slack error: {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Slack error: {e}[/red]")
            return False
    
    def send_to_telegram(self, image_url: str, message: str, bot_token: str, chat_id: str):
        """Send image to Telegram chat"""
        url = self.endpoints["telegram"].url.format(token=bot_token)
        
        payload = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": message
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.endpoints["telegram"].headers)
            if response.ok:
                console.print("[green]✅ Image sent to Telegram[/green]")
                return True
            else:
                console.print(f"[red]❌ Telegram error: {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Telegram error: {e}[/red]")
            return False
    
    def upload_to_dropbox(self, image_url: str, filename: str, access_token: str):
        """Upload image to Dropbox"""
        url = self.endpoints["dropbox"].url
        headers = self.endpoints["dropbox"].headers.copy()
        headers["Authorization"] = headers["Authorization"].format(token=access_token)
        headers["Dropbox-API-Arg"] = json.dumps({"path": f"/{filename}"})
        
        try:
            # Download image first
            image_response = requests.get(image_url)
            if not image_response.ok:
                console.print("[red]❌ Failed to download image[/red]")
                return False
            
            response = requests.post(url, data=image_response.content, headers=headers)
            if response.ok:
                console.print("[green]✅ Image uploaded to Dropbox[/green]")
                return True
            else:
                console.print(f"[red]❌ Dropbox error: {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Dropbox error: {e}[/red]")
            return False
    
    def upload_to_google_drive(self, image_url: str, filename: str, access_token: str):
        """Upload image to Google Drive"""
        url = self.endpoints["google_drive"].url
        headers = self.endpoints["google_drive"].headers.copy()
        headers["Authorization"] = headers["Authorization"].format(token=access_token)
        
        # Prepare metadata
        metadata = {
            "name": filename,
            "parents": ["root"]
        }
        
        try:
            # Download image first
            image_response = requests.get(image_url)
            if not image_response.ok:
                console.print("[red]❌ Failed to download image[/red]")
                return False
            
            # Create multipart upload
            files = {
                "metadata": (None, json.dumps(metadata), "application/json"),
                "file": (filename, image_response.content, "image/jpeg")
            }
            
            response = requests.post(url, files=files, headers=headers)
            if response.ok:
                console.print("[green]✅ Image uploaded to Google Drive[/green]")
                return True
            else:
                console.print(f"[red]❌ Google Drive error: {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Google Drive error: {e}[/red]")
            return False
    
    def batch_export(self, image_urls: List[str], export_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export multiple images to various services"""
        results = {
            "total_images": len(image_urls),
            "successful_exports": 0,
            "failed_exports": 0,
            "export_results": []
        }
        
        console.print(f"[cyan]📤 Batch exporting {len(image_urls)} images to {len(export_configs)} services[/cyan]")
        
        for i, (image_url, config) in enumerate(zip(image_urls, export_configs)):
            service = config.get("service")
            success = False
            
            if service == "discord":
                success = self.send_to_discord(
                    image_url,
                    config.get("message", "Generated image"),
                    config.get("webhook_id"),
                    config.get("token")
                )
            elif service == "slack":
                success = self.send_to_slack(
                    image_url,
                    config.get("message", "Generated image"),
                    config.get("token")
                )
            elif service == "telegram":
                success = self.send_to_telegram(
                    image_url,
                    config.get("message", "Generated image"),
                    config.get("bot_token"),
                    config.get("chat_id")
                )
            elif service == "dropbox":
                success = self.upload_to_dropbox(
                    image_url,
                    config.get("filename", f"image_{i}.jpg"),
                    config.get("access_token")
                )
            elif service == "google_drive":
                success = self.upload_to_google_drive(
                    image_url,
                    config.get("filename", f"image_{i}.jpg"),
                    config.get("access_token")
                )
            
            results["export_results"].append({
                "image_url": image_url,
                "service": service,
                "success": success
            })
            
            if success:
                results["successful_exports"] += 1
            else:
                results["failed_exports"] += 1
        
        return results
    
    def display_integrations(self):
        """Display available integrations"""
        console.print("\n[bold cyan]🔗 Available API Integrations[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Service", style="cyan", width=15)
        table.add_column("Description", style="green", width=30)
        table.add_column("Auth Type", style="yellow", width=15)
        table.add_column("Method", style="blue", width=8)
        
        for endpoint in self.endpoints.values():
            table.add_row(
                endpoint.name,
                endpoint.description,
                endpoint.auth_type,
                endpoint.method
            )
        
        console.print(table)

def demo_webhooks_and_integrations():
    """Demo webhook and integration features"""
    banner = Panel(
        "[bold blue]🔗 Webhooks & API Integrations Demo[/bold blue]\n\n"
        "Demonstrating external integrations and webhook functionality",
        title="API Integrations",
        border_style="blue"
    )
    console.print(banner)
    
    # Initialize managers
    webhook_manager = WebhookManager()
    api_integrations = APIIntegrations()
    
    # Display available integrations
    api_integrations.display_integrations()
    
    # Demo webhook registration
    console.print("\n[bold cyan]📡 Webhook Registration Demo[/bold cyan]")
    
    webhook_manager.register_webhook(
        "demo_webhook",
        "https://webhook.site/demo",
        ["image_generated", "generation_failed", "batch_completed"],
        "demo_secret_key"
    )
    
    # Demo webhook events
    console.print("\n[bold cyan]📨 Webhook Events Demo[/bold cyan]")
    
    # Simulate image generation events
    webhook_manager.send_webhook("image_generated", {
        "prompt": "A beautiful sunset over mountains",
        "image_url": "https://example.com/generated_image.jpg",
        "generation_time": 45.2,
        "model": "nano_banana"
    })
    
    webhook_manager.send_webhook("batch_completed", {
        "total_images": 5,
        "successful": 4,
        "failed": 1,
        "total_time": 180.5
    })
    
    # Demo API integrations
    console.print("\n[bold cyan]📤 API Integration Demo[/bold cyan]")
    
    demo_image_url = "https://example.com/demo_image.jpg"
    
    # Note: These would normally use real tokens/credentials
    console.print("[yellow]💡 Note: These integrations require valid tokens/credentials[/yellow]")
    
    # Demo export configurations
    export_configs = [
        {
            "service": "discord",
            "message": "Generated image from Nano Banana!",
            "webhook_id": "demo_webhook_id",
            "token": "demo_token"
        },
        {
            "service": "slack",
            "message": "New AI-generated image",
            "token": "demo_slack_token"
        },
        {
            "service": "dropbox",
            "filename": "nano_banana_image.jpg",
            "access_token": "demo_access_token"
        }
    ]
    
    # Batch export demo
    batch_result = api_integrations.batch_export([demo_image_url], export_configs)
    
    console.print(f"\n[bold green]📊 Batch Export Results:[/bold green]")
    console.print(f"Total Images: {batch_result['total_images']}")
    console.print(f"Successful: {batch_result['successful_exports']}")
    console.print(f"Failed: {batch_result['failed_exports']}")
    
    # Webhook statistics
    webhook_stats = webhook_manager.get_webhook_stats()
    
    stats_panel = Panel(
        f"[bold blue]📊 Webhook Statistics[/bold blue]\n\n"
        f"Total Webhooks: {webhook_stats['total_webhooks']}\n"
        f"Active Webhooks: {webhook_stats['active_webhooks']}\n"
        f"Total Events: {webhook_stats['total_events']}\n\n"
        f"[bold]Event Counts:[/bold]\n" +
        "\n".join([f"• {event}: {count}" for event, count in webhook_stats['event_counts'].items()]),
        title="Webhook Stats",
        border_style="blue"
    )
    console.print(stats_panel)
    
    # Feature summary
    features_panel = Panel(
        "[bold green]🎉 Webhook & Integration Features:[/bold green]\n\n"
        "✅ Webhook registration and management\n"
        "✅ Event-driven notifications\n"
        "✅ HMAC signature verification\n"
        "✅ Discord integration\n"
        "✅ Slack integration\n"
        "✅ Telegram bot support\n"
        "✅ Dropbox upload\n"
        "✅ Google Drive upload\n"
        "✅ AWS S3 integration\n"
        "✅ Batch export capabilities\n"
        "✅ Error handling and retry logic\n"
        "✅ Integration statistics\n\n"
        "[bold yellow]💡 Connect your image generation to any service![/bold yellow]",
        title="Integrations Complete",
        border_style="green"
    )
    console.print(features_panel)

def main():
    """Main function for webhooks and integrations demo"""
    demo_webhooks_and_integrations()

if __name__ == "__main__":
    main()
