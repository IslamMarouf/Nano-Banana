#!/usr/bin/env python3
"""
Analytics dashboard for Nano Banana Image Generator
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import requests

console = Console()

class AnalyticsDashboard:
    def __init__(self, api_base: str = "http://127.0.0.1:10000"):
        self.api_base = api_base
        self.stats_file = Path("generation_stats.json")
        self.history_file = Path("generation_history.json")
    
    def load_stats(self) -> Dict[str, Any]:
        """Load generation statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load stats: {e}[/yellow]")
        
        return {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "last_updated": None
        }
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load generation history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load history: {e}[/yellow]")
        
        return []
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get current server statistics"""
        try:
            response = requests.get(f"{self.api_base}/v1/stats", timeout=5)
            if response.ok:
                return response.json()
        except Exception:
            pass
        
        return {}
    
    def analyze_prompts(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze prompt patterns"""
        if not history:
            return {"total_prompts": 0, "unique_prompts": 0, "common_words": []}
        
        # Count prompt types
        create_count = len([h for h in history if h.get("type") == "create"])
        edit_count = len([h for h in history if h.get("type") == "edit"])
        
        # Analyze words in prompts
        all_words = []
        for item in history:
            words = item.get("prompt", "").lower().split()
            all_words.extend(words)
        
        # Count word frequency
        word_count = {}
        for word in all_words:
            if len(word) > 3:  # Ignore short words
                word_count[word] = word_count.get(word, 0) + 1
        
        # Get most common words
        common_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_prompts": len(history),
            "create_count": create_count,
            "edit_count": edit_count,
            "unique_prompts": len(set(item.get("prompt", "") for item in history)),
            "common_words": common_words,
            "average_prompt_length": sum(len(item.get("prompt", "")) for item in history) / len(history) if history else 0
        }
    
    def analyze_formats(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze format usage"""
        format_count = {}
        for item in history:
            format_type = item.get("format", "jpg")
            format_count[format_type] = format_count.get(format_type, 0) + 1
        
        return format_count
    
    def analyze_resolutions(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze resolution usage"""
        resolution_count = {}
        for item in history:
            resolution = item.get("resolution", "1024x1024")
            resolution_count[resolution] = resolution_count.get(resolution, 0) + 1
        
        return resolution_count
    
    def get_time_analysis(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze generation patterns over time"""
        if not history:
            return {"hourly": {}, "daily": {}}
        
        # Group by hour and day
        hourly = {}
        daily = {}
        
        for item in history:
            timestamp = item.get("timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    day = dt.strftime("%Y-%m-%d")
                    
                    hourly[hour] = hourly.get(hour, 0) + 1
                    daily[day] = daily.get(day, 0) + 1
                except:
                    continue
        
        return {"hourly": hourly, "daily": daily}
    
    def create_summary_panel(self, stats: Dict[str, Any], server_stats: Dict[str, Any]) -> Panel:
        """Create summary statistics panel"""
        total = stats.get("total_generations", 0)
        successful = stats.get("successful_generations", 0)
        failed = stats.get("failed_generations", 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        server_uptime = server_stats.get("server_uptime", 0)
        uptime_str = "Unknown"
        if server_uptime:
            uptime_seconds = int(time.time()) - server_uptime
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            uptime_str = f"{hours}h {minutes}m"
        
        content = f"""
[bold blue]📊 Generation Statistics[/bold blue]

Total Generations: [bold]{total}[/bold]
Successful: [bold green]{successful}[/bold green]
Failed: [bold red]{failed}[/bold red]
Success Rate: [bold]{success_rate:.1f}%[/bold]

Server Uptime: [bold]{uptime_str}[/bold]
Last Updated: [bold]{stats.get('last_updated', 'Never')}[/bold]
        """
        
        return Panel(content.strip(), title="Summary", border_style="blue")
    
    def create_prompt_analysis_panel(self, prompt_analysis: Dict[str, Any]) -> Panel:
        """Create prompt analysis panel"""
        content = f"""
[bold cyan]📝 Prompt Analysis[/bold cyan]

Total Prompts: [bold]{prompt_analysis['total_prompts']}[/bold]
Unique Prompts: [bold]{prompt_analysis['unique_prompts']}[/bold]
Create vs Edit: [bold green]{prompt_analysis['create_count']}[/bold green] / [bold yellow]{prompt_analysis['edit_count']}[/bold yellow]
Avg Length: [bold]{prompt_analysis['average_prompt_length']:.0f} chars[/bold]

[bold]Most Common Words:[/bold]
        """
        
        for word, count in prompt_analysis['common_words'][:5]:
            content += f"\n• {word}: {count}"
        
        return Panel(content.strip(), title="Prompts", border_style="cyan")
    
    def create_format_analysis_panel(self, format_analysis: Dict[str, int], resolution_analysis: Dict[str, int]) -> Panel:
        """Create format and resolution analysis panel"""
        content = "[bold magenta]🖼️ Format & Resolution Analysis[/bold magenta]\n\n"
        
        content += "[bold]Formats:[/bold]\n"
        for format_type, count in sorted(format_analysis.items(), key=lambda x: x[1], reverse=True):
            content += f"• {format_type.upper()}: {count}\n"
        
        content += "\n[bold]Resolutions:[/bold]\n"
        for resolution, count in sorted(resolution_analysis.items(), key=lambda x: x[1], reverse=True):
            content += f"• {resolution}: {count}\n"
        
        return Panel(content.strip(), title="Formats & Resolutions", border_style="magenta")
    
    def create_time_analysis_table(self, time_analysis: Dict[str, Any]) -> Table:
        """Create time analysis table"""
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Time", style="cyan", width=15)
        table.add_column("Count", style="yellow", width=10)
        table.add_column("Visual", style="green", width=20)
        
        # Show hourly data
        hourly = time_analysis.get("hourly", {})
        if hourly:
            max_count = max(hourly.values()) if hourly.values() else 1
            
            for hour in sorted(hourly.keys()):
                count = hourly[hour]
                bar_length = int((count / max_count) * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                
                table.add_row(
                    f"{hour:02d}:00",
                    str(count),
                    f"[green]{bar}[/green]"
                )
        
        return table
    
    def create_recent_activity_table(self, history: List[Dict[str, Any]]) -> Table:
        """Create recent activity table"""
        table = Table(show_header=True, header_style="bold red")
        table.add_column("Time", style="cyan", width=20)
        table.add_column("Type", style="green", width=8)
        table.add_column("Prompt", style="yellow", width=40)
        table.add_column("Format", style="blue", width=8)
        table.add_column("Status", style="red", width=8)
        
        # Show last 10 entries
        recent = history[:10]
        
        for item in recent:
            timestamp = item.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%m/%d %H:%M")
            except:
                time_str = "Unknown"
            
            item_type = item.get("type", "unknown")
            prompt = item.get("prompt", "")[:40] + "..." if len(item.get("prompt", "")) > 40 else item.get("prompt", "")
            format_type = item.get("format", "jpg").upper()
            status = "✅" if item.get("url") else "❌"
            
            table.add_row(time_str, item_type, prompt, format_type, status)
        
        return table
    
    def display_dashboard(self):
        """Display the complete analytics dashboard"""
        # Load data
        stats = self.load_stats()
        history = self.load_history()
        server_stats = self.get_server_stats()
        
        # Analyze data
        prompt_analysis = self.analyze_prompts(history)
        format_analysis = self.analyze_formats(history)
        resolution_analysis = self.analyze_resolutions(history)
        time_analysis = self.get_time_analysis(history)
        
        # Clear screen and show banner
        console.clear()
        banner = Panel(
            "[bold blue]🍌 Nano Banana Analytics Dashboard[/bold blue]\n\n"
            "Real-time generation analytics and insights",
            title="Analytics",
            border_style="blue"
        )
        console.print(banner)
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="top", size=3),
            Layout(name="middle", size=15),
            Layout(name="bottom")
        )
        
        layout["middle"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="summary", size=8),
            Layout(name="prompts", size=10)
        )
        
        layout["right"].split_column(
            Layout(name="formats", size=8),
            Layout(name="time", size=10)
        )
        
        # Populate layout
        layout["top"].update(self.create_recent_activity_table(history))
        layout["summary"].update(self.create_summary_panel(stats, server_stats))
        layout["prompts"].update(self.create_prompt_analysis_panel(prompt_analysis))
        layout["formats"].update(self.create_format_analysis_panel(format_analysis, resolution_analysis))
        layout["time"].update(self.create_time_analysis_table(time_analysis))
        
        # Display layout
        console.print(layout)
        
        # Show footer
        footer = Panel(
            f"[bold]Last Updated:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"[bold]Total History Items:[/bold] {len(history)} | "
            f"[bold]Press Ctrl+C to exit[/bold]",
            border_style="blue"
        )
        console.print(footer)
    
    def run_live_dashboard(self, refresh_interval: int = 30):
        """Run live dashboard with auto-refresh"""
        try:
            with Live(self.display_dashboard, refresh_per_second=1, screen=True) as live:
                while True:
                    time.sleep(refresh_interval)
                    live.update(self.display_dashboard())
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard stopped[/yellow]")

def main():
    """Main function for analytics dashboard"""
    dashboard = AnalyticsDashboard()
    
    console.print("[bold cyan]Choose dashboard mode:[/bold cyan]")
    console.print("1. Static dashboard (show once)")
    console.print("2. Live dashboard (auto-refresh every 30s)")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        dashboard.display_dashboard()
    elif choice == "2":
        console.print("[green]Starting live dashboard... Press Ctrl+C to stop[/green]")
        dashboard.run_live_dashboard()
    else:
        console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main()
