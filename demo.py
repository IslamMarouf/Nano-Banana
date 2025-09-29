#!/usr/bin/env python3
"""
Demo script to showcase Nano Banana Image Generator features
"""

import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from config_manager import config

console = Console()

def demo_banner():
    """Display demo banner"""
    banner = Panel(
        "[bold blue]🍌 Nano Banana Image Generator - Feature Demo[/bold blue]\n\n"
        "This demo showcases the enhanced features of the application",
        title="Demo Mode",
        border_style="blue"
    )
    console.print(banner)

def demo_configuration():
    """Demo configuration features"""
    console.print("\n[bold cyan]📋 Configuration Features Demo[/bold cyan]")
    
    # Show current config
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Current Value", style="green")
    table.add_column("Type", style="yellow")
    
    settings = [
        ("Output Format", config.get('default_settings', 'output_format', 'jpg'), "String"),
        ("Resolution", config.get('default_settings', 'resolution', '1024x1024'), "String"),
        ("Quality", config.get('default_settings', 'quality', 'high'), "String"),
        ("Show Progress", str(config.get('ui_settings', 'show_progress', True)), "Boolean"),
        ("Fallback Enabled", str(config.get('advanced_settings', 'fallback_enabled', True)), "Boolean"),
    ]
    
    for setting, value, type_info in settings:
        table.add_row(setting, value, type_info)
    
    console.print(table)
    
    # Demo config changes
    console.print("\n[bold yellow]🔄 Demonstrating configuration changes...[/bold yellow]")
    
    original_format = config.get('default_settings', 'output_format', 'jpg')
    console.print(f"Original format: {original_format}")
    
    # Change format
    config.set('default_settings', 'output_format', 'png')
    console.print("✅ Changed format to PNG")
    
    # Change it back
    config.set('default_settings', 'output_format', original_format)
    console.print(f"✅ Restored format to {original_format}")

def demo_progress_bars():
    """Demo progress bar features"""
    console.print("\n[bold cyan]📊 Progress Bar Features Demo[/bold cyan]")
    
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    
    # Demo different progress styles
    progress_styles = [
        ("Basic Progress", [SpinnerColumn(), TextColumn("[progress.description]{task.description}")]),
        ("Progress with Bar", [SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn()]),
        ("Full Progress", [SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), TimeElapsedColumn()])
    ]
    
    for style_name, columns in progress_styles:
        console.print(f"\n[bold yellow]Demo: {style_name}[/bold yellow]")
        
        with Progress(*columns, console=console) as progress:
            task = progress.add_task(f"Demoing {style_name.lower()}...", total=100)
            
            for i in range(0, 101, 10):
                progress.update(task, advance=10, description=f"{style_name}... ({i}%)")
                time.sleep(0.1)
        
        console.print(f"✅ {style_name} completed")

def demo_error_handling():
    """Demo improved error handling"""
    console.print("\n[bold cyan]⚠️  Error Handling Demo[/bold cyan]")
    
    from rich.panel import Panel
    
    # Demo different error types
    error_examples = [
        ("Network Error", "Connection error - unable to reach the image server"),
        ("File System Error", "File system error: Permission denied"),
        ("HTTP Error", "HTTP error 404: Not Found"),
        ("Timeout Error", "Request timed out - the image server is taking too long to respond")
    ]
    
    for error_type, error_message in error_examples:
        error_panel = Panel(
            f"[bold red]❌ {error_type}[/bold red]\n\n"
            f"[yellow]{error_message}[/yellow]\n\n"
            f"[cyan]This demonstrates improved error messages with specific details and helpful suggestions.[/cyan]",
            title=f"{error_type} Example",
            border_style="red"
        )
        console.print(error_panel)
        time.sleep(1)

def demo_image_formats():
    """Demo image format support"""
    console.print("\n[bold cyan]🖼️  Image Format Support Demo[/bold cyan]")
    
    from utils import get_image_format_from_url
    
    test_urls = [
        "https://example.com/image.jpg",
        "https://example.com/photo.png",
        "https://example.com/picture.webp",
        "https://example.com/graphic.jpeg",
        "https://example.com/unknown"
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("URL", style="cyan")
    table.add_column("Detected Format", style="green")
    table.add_column("Status", style="yellow")
    
    for url in test_urls:
        detected = get_image_format_from_url(url)
        status = "✅ Detected" if detected != "jpg" or url.endswith(('.jpg', '.jpeg')) else "⚠️  Default"
        table.add_row(url, detected, status)
    
    console.print(table)

def main():
    """Run the demo"""
    demo_banner()
    
    # Run all demos
    demo_configuration()
    demo_progress_bars()
    demo_error_handling()
    demo_image_formats()
    
    # Final message
    final_panel = Panel(
        "[bold green]🎉 Demo completed successfully![/bold green]\n\n"
        "The Nano Banana Image Generator now features:\n"
        "• Beautiful progress bars with Rich library\n"
        "• Persistent configuration management\n"
        "• Multiple image format support\n"
        "• Enhanced error handling\n"
        "• Interactive settings menu\n\n"
        "Run 'python app.py' to try the enhanced interface!",
        title="Demo Complete",
        border_style="green"
    )
    console.print(final_panel)

if __name__ == "__main__":
    main()

