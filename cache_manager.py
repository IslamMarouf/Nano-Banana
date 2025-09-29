#!/usr/bin/env python3
"""
Caching system for Nano Banana Image Generator
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import shutil

console = Console()

class CacheManager:
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_index()
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)
    
    def _load_index(self) -> Dict[str, Any]:
        """Load cache index from file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load cache index: {e}[/yellow]")
        
        return {
            "entries": {},
            "metadata": {
                "created": time.time(),
                "last_cleanup": time.time(),
                "total_size_bytes": 0
            }
        }
    
    def _save_index(self):
        """Save cache index to file"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving cache index: {e}[/red]")
    
    def _generate_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key from prompt and parameters"""
        # Create a hash from prompt and parameters
        content = f"{prompt}|{kwargs.get('format', 'jpg')}|{kwargs.get('resolution', '1024x1024')}|{kwargs.get('quality', 'high')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache entry"""
        return self.cache_dir / f"{key}.json"
    
    def _get_image_path(self, key: str, extension: str = "jpg") -> Path:
        """Get image file path for cache entry"""
        return self.cache_dir / f"{key}.{extension}"
    
    def _get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total_size = 0
        for file_path in self.cache_dir.glob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def _get_cache_size_mb(self) -> float:
        """Get total cache size in MB"""
        return self._get_cache_size() / (1024 * 1024)
    
    def _cleanup_cache(self):
        """Clean up cache if it exceeds max size"""
        current_size_mb = self._get_cache_size_mb()
        
        if current_size_mb > self.max_size_mb:
            console.print(f"[yellow]Cache size ({current_size_mb:.1f}MB) exceeds limit ({self.max_size_mb}MB). Cleaning up...[/yellow]")
            
            # Sort entries by access time (oldest first)
            entries = list(self.cache_index["entries"].items())
            entries.sort(key=lambda x: x[1].get("last_accessed", 0))
            
            # Remove oldest entries until under limit
            for key, entry in entries:
                if current_size_mb <= self.max_size_mb * 0.8:  # Clean to 80% of limit
                    break
                
                # Remove files
                cache_file = self._get_cache_path(key)
                image_file = self._get_image_path(key, entry.get("extension", "jpg"))
                
                for file_path in [cache_file, image_file]:
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        current_size_mb -= file_size / (1024 * 1024)
                
                # Remove from index
                del self.cache_index["entries"][key]
            
            # Update metadata
            self.cache_index["metadata"]["last_cleanup"] = time.time()
            self.cache_index["metadata"]["total_size_bytes"] = self._get_cache_size()
            self._save_index()
            
            console.print(f"[green]Cache cleanup completed. New size: {current_size_mb:.1f}MB[/green]")
    
    def get(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached result for prompt"""
        key = self._generate_key(prompt, **kwargs)
        
        if key in self.cache_index["entries"]:
            entry = self.cache_index["entries"][key]
            cache_file = self._get_cache_path(key)
            
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    
                    # Update access time
                    entry["last_accessed"] = time.time()
                    self.cache_index["entries"][key] = entry
                    self._save_index()
                    
                    console.print(f"[green]✅ Cache hit for prompt: {prompt[:50]}...[/green]")
                    return cached_data
                    
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not read cache file: {e}[/yellow]")
                    # Remove invalid entry
                    del self.cache_index["entries"][key]
                    self._save_index()
        
        return None
    
    def set(self, prompt: str, result: Dict[str, Any], **kwargs):
        """Cache result for prompt"""
        key = self._generate_key(prompt, **kwargs)
        
        # Prepare cache entry
        entry = {
            "prompt": prompt,
            "created": time.time(),
            "last_accessed": time.time(),
            "extension": kwargs.get("format", "jpg"),
            "resolution": kwargs.get("resolution", "1024x1024"),
            "quality": kwargs.get("quality", "high")
        }
        
        # Save cache data
        cache_file = self._get_cache_path(key)
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Update index
            self.cache_index["entries"][key] = entry
            self.cache_index["metadata"]["total_size_bytes"] = self._get_cache_size()
            self._save_index()
            
            console.print(f"[green]✅ Cached result for prompt: {prompt[:50]}...[/green]")
            
            # Check if cleanup is needed
            self._cleanup_cache()
            
        except Exception as e:
            console.print(f"[red]Error caching result: {e}[/red]")
    
    def download_and_cache_image(self, image_url: str, prompt: str, **kwargs) -> Optional[str]:
        """Download image and cache it locally"""
        import requests
        
        key = self._generate_key(prompt, **kwargs)
        extension = kwargs.get("format", "jpg")
        image_file = self._get_image_path(key, extension)
        
        if image_file.exists():
            console.print(f"[green]✅ Image already cached: {image_file.name}[/green]")
            return str(image_file)
        
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(image_file, 'wb') as f:
                f.write(response.content)
            
            console.print(f"[green]✅ Downloaded and cached image: {image_file.name}[/green]")
            return str(image_file)
            
        except Exception as e:
            console.print(f"[red]Error downloading image: {e}[/red]")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        entries = self.cache_index["entries"]
        total_size_mb = self._get_cache_size_mb()
        
        # Calculate age statistics
        now = time.time()
        ages = []
        for entry in entries.values():
            ages.append(now - entry["created"])
        
        stats = {
            "total_entries": len(entries),
            "total_size_mb": round(total_size_mb, 2),
            "max_size_mb": self.max_size_mb,
            "usage_percentage": round((total_size_mb / self.max_size_mb) * 100, 1),
            "oldest_entry_age_hours": round(max(ages) / 3600, 1) if ages else 0,
            "newest_entry_age_hours": round(min(ages) / 3600, 1) if ages else 0,
            "cache_created": self.cache_index["metadata"]["created"],
            "last_cleanup": self.cache_index["metadata"]["last_cleanup"]
        }
        
        return stats
    
    def display_stats(self):
        """Display cache statistics in a nice table"""
        stats = self.get_cache_stats()
        
        # Summary panel
        summary_panel = Panel(
            f"[bold blue]📊 Cache Statistics[/bold blue]\n\n"
            f"Entries: [bold]{stats['total_entries']}[/bold]\n"
            f"Size: [bold]{stats['total_size_mb']}MB[/bold] / {stats['max_size_mb']}MB ({stats['usage_percentage']}%)\n"
            f"Oldest: [bold]{stats['oldest_entry_age_hours']}h[/bold]\n"
            f"Newest: [bold]{stats['newest_entry_age_hours']}h[/bold]",
            title="Cache Overview",
            border_style="blue"
        )
        console.print(summary_panel)
        
        # Detailed table
        if stats['total_entries'] > 0:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Prompt", style="cyan", width=40)
            table.add_column("Format", style="green", width=8)
            table.add_column("Resolution", style="yellow", width=12)
            table.add_column("Age (h)", style="blue", width=10)
            table.add_column("Size (KB)", style="red", width=12)
            
            entries = self.cache_index["entries"]
            for key, entry in entries.items():
                # Get file size
                image_file = self._get_image_path(key, entry.get("extension", "jpg"))
                file_size_kb = round(image_file.stat().st_size / 1024, 1) if image_file.exists() else 0
                
                # Calculate age
                age_hours = round((time.time() - entry["created"]) / 3600, 1)
                
                table.add_row(
                    entry["prompt"][:40] + "..." if len(entry["prompt"]) > 40 else entry["prompt"],
                    entry.get("extension", "jpg").upper(),
                    entry.get("resolution", "1024x1024"),
                    str(age_hours),
                    str(file_size_kb)
                )
            
            console.print(table)
    
    def clear_cache(self, confirm: bool = False):
        """Clear all cache entries"""
        if not confirm:
            console.print("[red]This will delete all cached files. Are you sure? (y/n)[/red]")
            response = input().strip().lower()
            if response != 'y':
                console.print("[yellow]Cache clear cancelled[/yellow]")
                return
        
        # Remove all files
        for file_path in self.cache_dir.glob("*"):
            if file_path.is_file() and file_path.name != "cache_index.json":
                file_path.unlink()
        
        # Reset index
        self.cache_index = {
            "entries": {},
            "metadata": {
                "created": time.time(),
                "last_cleanup": time.time(),
                "total_size_bytes": 0
            }
        }
        self._save_index()
        
        console.print("[green]✅ Cache cleared successfully[/green]")
    
    def cleanup_old_entries(self, max_age_hours: int = 24):
        """Remove entries older than specified age"""
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        
        removed_count = 0
        for key, entry in list(self.cache_index["entries"].items()):
            if now - entry["created"] > max_age_seconds:
                # Remove files
                cache_file = self._get_cache_path(key)
                image_file = self._get_image_path(key, entry.get("extension", "jpg"))
                
                for file_path in [cache_file, image_file]:
                    if file_path.exists():
                        file_path.unlink()
                
                # Remove from index
                del self.cache_index["entries"][key]
                removed_count += 1
        
        if removed_count > 0:
            self.cache_index["metadata"]["total_size_bytes"] = self._get_cache_size()
            self.cache_index["metadata"]["last_cleanup"] = time.time()
            self._save_index()
            console.print(f"[green]✅ Removed {removed_count} old cache entries[/green]")
        else:
            console.print("[yellow]No old entries to remove[/yellow]")

def main():
    """Main function for cache management"""
    banner = Panel(
        "[bold blue]🍌 Nano Banana Cache Manager[/bold blue]\n\n"
        "Manage cached images and generation results",
        title="Cache Management",
        border_style="blue"
    )
    console.print(banner)
    
    cache_manager = CacheManager()
    
    while True:
        console.print("\n[bold cyan]Cache Management Options:[/bold cyan]")
        console.print("1. View cache statistics")
        console.print("2. Clear all cache")
        console.print("3. Cleanup old entries")
        console.print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            cache_manager.display_stats()
        elif choice == "2":
            cache_manager.clear_cache()
        elif choice == "3":
            age = input("Enter max age in hours [24]: ").strip()
            max_age = int(age) if age.isdigit() else 24
            cache_manager.cleanup_old_entries(max_age)
        elif choice == "4":
            console.print("[green]Goodbye![/green]")
            break
        else:
            console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main()
