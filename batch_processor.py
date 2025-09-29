#!/usr/bin/env python3
"""
Batch processing utility for Nano Banana Image Generator
"""

import asyncio
import json
import time
from typing import List, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
import requests

console = Console()

class BatchProcessor:
    def __init__(self, api_base: str = "http://127.0.0.1:10000"):
        self.api_base = api_base
        self.results = []
    
    async def process_batch(self, prompts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple prompts in batch"""
        console.print(f"[bold cyan]Starting batch processing for {len(prompts)} prompts[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Processing batch...", total=len(prompts))
            
            for i, prompt in enumerate(prompts):
                progress.update(task, advance=1, description=f"Processing: {prompt[:50]}...")
                
                try:
                    # Make API request
                    response = requests.post(
                        f"{self.api_base}/v1/image/generations",
                        json={"prompt": prompt, **kwargs},
                        timeout=120
                    )
                    
                    if response.ok:
                        data = response.json()
                        image_url = data["data"][0]["url"]
                        
                        result = {
                            "prompt": prompt,
                            "url": image_url,
                            "status": "success",
                            "index": i,
                            "timestamp": time.time()
                        }
                        
                        self.results.append(result)
                        progress.update(task, description=f"✅ Success: {prompt[:30]}...")
                        
                    else:
                        error_result = {
                            "prompt": prompt,
                            "url": None,
                            "status": "failed",
                            "error": f"HTTP {response.status_code}",
                            "index": i,
                            "timestamp": time.time()
                        }
                        
                        self.results.append(error_result)
                        progress.update(task, description=f"❌ Failed: {prompt[:30]}...")
                
                except Exception as e:
                    error_result = {
                        "prompt": prompt,
                        "url": None,
                        "status": "failed",
                        "error": str(e),
                        "index": i,
                        "timestamp": time.time()
                    }
                    
                    self.results.append(error_result)
                    progress.update(task, description=f"❌ Error: {prompt[:30]}...")
                
                # Small delay between requests
                await asyncio.sleep(1)
        
        return self.results
    
    def save_results(self, filename: str = None) -> str:
        """Save batch results to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"batch_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"[green]✅ Results saved to {filename}[/green]")
        return filename
    
    def display_results(self):
        """Display batch results in a nice table"""
        if not self.results:
            console.print("[yellow]No results to display[/yellow]")
            return
        
        success_count = len([r for r in self.results if r["status"] == "success"])
        failed_count = len(self.results) - success_count
        
        # Summary
        summary_panel = Panel(
            f"[bold green]✅ Successful: {success_count}[/bold green]\n"
            f"[bold red]❌ Failed: {failed_count}[/bold red]\n"
            f"[bold blue]📊 Total: {len(self.results)}[/bold blue]",
            title="Batch Processing Results",
            border_style="green" if failed_count == 0 else "yellow"
        )
        console.print(summary_panel)
        
        # Detailed table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Status", style="green", width=8)
        table.add_column("Prompt", style="yellow", width=40)
        table.add_column("URL", style="blue", width=30)
        table.add_column("Error", style="red", width=20)
        
        for result in self.results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            url_short = result["url"][:30] + "..." if result["url"] and len(result["url"]) > 30 else result["url"] or "N/A"
            error_text = result.get("error", "")[:20] if result.get("error") else ""
            
            table.add_row(
                str(result["index"]),
                status_icon,
                result["prompt"][:40] + "..." if len(result["prompt"]) > 40 else result["prompt"],
                url_short,
                error_text
            )
        
        console.print(table)
    
    def download_images(self, output_dir: str = "batch_output"):
        """Download all successful images"""
        Path(output_dir).mkdir(exist_ok=True)
        
        successful_results = [r for r in self.results if r["status"] == "success"]
        
        if not successful_results:
            console.print("[yellow]No successful images to download[/yellow]")
            return
        
        console.print(f"[cyan]Downloading {len(successful_results)} images to {output_dir}/[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading images...", total=len(successful_results))
            
            for i, result in enumerate(successful_results):
                try:
                    progress.update(task, advance=1, description=f"Downloading image {i+1}...")
                    
                    response = requests.get(result["url"], timeout=30)
                    response.raise_for_status()
                    
                    # Generate filename
                    prompt_clean = "".join(c for c in result["prompt"][:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{i+1:03d}_{prompt_clean}.jpg"
                    filepath = Path(output_dir) / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                except Exception as e:
                    console.print(f"[red]Failed to download image {i+1}: {e}[/red]")
        
        console.print(f"[green]✅ Images downloaded to {output_dir}/[/green]")

def load_prompts_from_file(filename: str) -> List[str]:
    """Load prompts from a text file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f.readlines() if line.strip()]
        
        console.print(f"[green]✅ Loaded {len(prompts)} prompts from {filename}[/green]")
        return prompts
    
    except FileNotFoundError:
        console.print(f"[red]❌ File not found: {filename}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]❌ Error loading prompts: {e}[/red]")
        return []

def create_sample_prompts_file():
    """Create a sample prompts file"""
    sample_prompts = [
        "A beautiful sunset over mountains",
        "A futuristic city with flying cars",
        "A cute cat sitting in a garden",
        "An abstract painting with vibrant colors",
        "A peaceful lake with swans",
        "A medieval castle on a hill",
        "A space station orbiting Earth",
        "A vintage car on a country road",
        "A magical forest with glowing trees",
        "A cozy cabin in the woods"
    ]
    
    filename = "sample_prompts.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample_prompts))
    
    console.print(f"[green]✅ Created sample prompts file: {filename}[/green]")
    return filename

async def main():
    """Main function for batch processing"""
    banner = Panel(
        "[bold blue]🍌 Nano Banana Batch Processor[/bold blue]\n\n"
        "Process multiple image generation prompts efficiently",
        title="Batch Processing",
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
    
    # Get prompts
    console.print("\n[bold cyan]Choose input method:[/bold cyan]")
    console.print("1. Load from file")
    console.print("2. Create sample prompts file")
    console.print("3. Enter prompts manually")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    prompts = []
    
    if choice == "1":
        filename = input("Enter prompts file path: ").strip()
        prompts = load_prompts_from_file(filename)
    elif choice == "2":
        filename = create_sample_prompts_file()
        prompts = load_prompts_from_file(filename)
    elif choice == "3":
        console.print("Enter prompts (one per line, empty line to finish):")
        while True:
            prompt = input("Prompt: ").strip()
            if not prompt:
                break
            prompts.append(prompt)
    else:
        console.print("[red]Invalid choice[/red]")
        return
    
    if not prompts:
        console.print("[yellow]No prompts to process[/yellow]")
        return
    
    # Get additional options
    format_choice = input("Output format (jpg/png/webp) [jpg]: ").strip() or "jpg"
    resolution_choice = input("Resolution (512x512/1024x1024/2048x2048) [1024x1024]: ").strip() or "1024x1024"
    
    # Process batch
    processor = BatchProcessor()
    results = await processor.process_batch(
        prompts,
        format=format_choice,
        resolution=resolution_choice
    )
    
    # Display results
    processor.display_results()
    
    # Save results
    save_choice = input("\nSave results to file? (y/n) [y]: ").strip().lower()
    if save_choice != 'n':
        processor.save_results()
    
    # Download images
    download_choice = input("Download successful images? (y/n) [y]: ").strip().lower()
    if download_choice != 'n':
        processor.download_images()
    
    console.print("\n[bold green]🎉 Batch processing completed![/bold green]")

if __name__ == "__main__":
    asyncio.run(main())
