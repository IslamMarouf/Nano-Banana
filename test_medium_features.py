#!/usr/bin/env python3
"""
Test script for medium-priority features of Nano Banana Image Generator
"""

import requests
import time
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_web_interface():
    """Test web interface availability"""
    console.print("\n[bold cyan]🌐 Testing Web Interface[/bold cyan]")
    
    try:
        response = requests.get("http://127.0.0.1:10000/web", timeout=5)
        if response.status_code == 200:
            console.print("✅ Web interface is accessible")
            console.print("🔗 Open http://127.0.0.1:10000/web in your browser")
            return True
        else:
            console.print(f"❌ Web interface returned status: {response.status_code}")
            return False
    except Exception as e:
        console.print(f"❌ Web interface error: {e}")
        return False

def test_batch_api():
    """Test batch processing API"""
    console.print("\n[bold cyan]📦 Testing Batch Processing API[/bold cyan]")
    
    test_prompts = [
        "A beautiful sunset over mountains",
        "A cute cat sitting in a garden"
    ]
    
    try:
        response = requests.post(
            "http://127.0.0.1:10000/v1/image/batch",
            json={
                "prompts": test_prompts,
                "format": "jpg",
                "resolution": "1024x1024"
            },
            timeout=60
        )
        
        if response.ok:
            data = response.json()
            console.print(f"✅ Batch API working")
            console.print(f"📊 Processed {data['total']} prompts")
            console.print(f"✅ Successful: {data['successful']}")
            console.print(f"❌ Failed: {data['failed']}")
            return True
        else:
            console.print(f"❌ Batch API failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"❌ Batch API error: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    console.print("\n[bold cyan]📁 Testing File Upload[/bold cyan]")
    
    # Create a test image file (simple text file for testing)
    test_file_content = b"fake image content for testing"
    test_filename = "test_image.jpg"
    
    try:
        files = {"file": (test_filename, test_file_content, "image/jpeg")}
        response = requests.post(
            "http://127.0.0.1:10000/upload",
            files=files,
            timeout=30
        )
        
        if response.ok:
            data = response.json()
            console.print("✅ File upload working")
            console.print(f"🔗 Upload URL: {data.get('url', 'N/A')}")
            return True
        else:
            console.print(f"❌ File upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"❌ File upload error: {e}")
        return False

def test_history_api():
    """Test history tracking API"""
    console.print("\n[bold cyan]📚 Testing History API[/bold cyan]")
    
    try:
        # Get history
        response = requests.get("http://127.0.0.1:10000/v1/history", timeout=5)
        if response.ok:
            data = response.json()
            console.print("✅ History GET working")
            console.print(f"📊 History entries: {len(data.get('history', []))}")
        else:
            console.print(f"❌ History GET failed: {response.status_code}")
            return False
        
        # Add test history item
        test_item = {
            "id": "test_" + str(int(time.time())),
            "type": "create",
            "prompt": "Test prompt for history",
            "format": "jpg",
            "resolution": "1024x1024",
            "image_url": "https://example.com/test.jpg",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "metadata": {"test": True}
        }
        
        response = requests.post(
            "http://127.0.0.1:10000/v1/history",
            json=test_item,
            timeout=5
        )
        
        if response.ok:
            console.print("✅ History POST working")
            return True
        else:
            console.print(f"❌ History POST failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"❌ History API error: {e}")
        return False

def test_stats_api():
    """Test statistics API"""
    console.print("\n[bold cyan]📊 Testing Statistics API[/bold cyan]")
    
    try:
        # Get stats
        response = requests.get("http://127.0.0.1:10000/v1/stats", timeout=5)
        if response.ok:
            data = response.json()
            console.print("✅ Stats GET working")
            console.print(f"📊 Total generations: {data.get('total_generations', 0)}")
            console.print(f"✅ Successful: {data.get('successful_generations', 0)}")
            console.print(f"❌ Failed: {data.get('failed_generations', 0)}")
        else:
            console.print(f"❌ Stats GET failed: {response.status_code}")
            return False
        
        # Update stats
        response = requests.post(
            "http://127.0.0.1:10000/v1/stats?success=true",
            timeout=5
        )
        
        if response.ok:
            console.print("✅ Stats POST working")
            return True
        else:
            console.print(f"❌ Stats POST failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"❌ Stats API error: {e}")
        return False

def test_enhanced_image_generation():
    """Test enhanced image generation with new parameters"""
    console.print("\n[bold cyan]🎨 Testing Enhanced Image Generation[/bold cyan]")
    
    try:
        response = requests.post(
            "http://127.0.0.1:10000/v1/image/generations",
            json={
                "prompt": "A beautiful test image with enhanced features",
                "format": "png",
                "resolution": "1024x1024",
                "quality": "high"
            },
            timeout=60
        )
        
        if response.ok:
            data = response.json()
            image_url = data["data"][0]["url"]
            console.print("✅ Enhanced image generation working")
            console.print(f"🔗 Generated image: {image_url}")
            console.print(f"📝 Revised prompt: {data['data'][0].get('revised_prompt', 'N/A')}")
            return True
        else:
            console.print(f"❌ Enhanced generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"❌ Enhanced generation error: {e}")
        return False

def display_api_endpoints():
    """Display all available API endpoints"""
    console.print("\n[bold cyan]🔗 Available API Endpoints[/bold cyan]")
    
    endpoints = [
        ("POST", "/v1/image/generations", "Generate single image"),
        ("POST", "/v1/image/batch", "Batch generate images"),
        ("POST", "/upload", "Upload file for editing"),
        ("GET", "/v1/history", "Get generation history"),
        ("POST", "/v1/history", "Add to history"),
        ("GET", "/v1/stats", "Get statistics"),
        ("POST", "/v1/stats", "Update statistics"),
        ("GET", "/web", "Web interface"),
        ("GET", "/health", "Health check"),
        ("GET", "/docs", "API documentation")
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan", width=8)
    table.add_column("Endpoint", style="green", width=25)
    table.add_column("Description", style="yellow", width=30)
    
    for method, endpoint, description in endpoints:
        table.add_row(method, endpoint, description)
    
    console.print(table)

def main():
    """Run all medium-priority feature tests"""
    banner = Panel(
        "[bold blue]🍌 Nano Banana - Medium Priority Features Test[/bold blue]\n\n"
        "Testing all new medium-priority enhancements",
        title="Feature Test",
        border_style="blue"
    )
    console.print(banner)
    
    # Check server status
    try:
        response = requests.get("http://127.0.0.1:10000/health", timeout=5)
        if not response.ok:
            raise Exception("Server not responding")
        console.print("[green]✅ Server is running[/green]")
    except Exception:
        console.print("[red]❌ Server not running. Please start with: python main.py[/red]")
        return
    
    # Display API endpoints
    display_api_endpoints()
    
    # Run tests
    test_results = []
    
    test_results.append(("Web Interface", test_web_interface()))
    test_results.append(("Batch Processing", test_batch_api()))
    test_results.append(("File Upload", test_file_upload()))
    test_results.append(("History Tracking", test_history_api()))
    test_results.append(("Statistics", test_stats_api()))
    test_results.append(("Enhanced Generation", test_enhanced_image_generation()))
    
    # Display results
    console.print("\n[bold cyan]📋 Test Results Summary[/bold cyan]")
    
    results_table = Table(show_header=True, header_style="bold magenta")
    results_table.add_column("Feature", style="cyan", width=20)
    results_table.add_column("Status", style="green", width=10)
    results_table.add_column("Icon", style="yellow", width=5)
    
    passed = 0
    for feature, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        icon = "✅" if result else "❌"
        if result:
            passed += 1
        results_table.add_row(feature, status, icon)
    
    console.print(results_table)
    
    # Final summary
    total = len(test_results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    final_panel = Panel(
        f"[bold green]🎉 Test Results: {passed}/{total} features working ({success_rate:.1f}%)[/bold green]\n\n"
        f"[bold blue]✨ Medium Priority Features Implemented:[/bold blue]\n"
        f"• Modern web interface with drag & drop\n"
        f"• Batch processing for multiple prompts\n"
        f"• File upload and caching system\n"
        f"• History tracking and analytics\n"
        f"• Enhanced API with statistics\n\n"
        f"[bold yellow]🌐 Web Interface:[/bold yellow] http://127.0.0.1:10000/web\n"
        f"[bold yellow]📚 API Docs:[/bold yellow] http://127.0.0.1:10000/docs",
        title="Test Complete",
        border_style="green" if passed == total else "yellow"
    )
    console.print(final_panel)

if __name__ == "__main__":
    main()
