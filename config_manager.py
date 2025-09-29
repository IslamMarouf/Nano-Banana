import json
import os
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    console.print(f"[green]✅ Configuration loaded from {self.config_file}[/green]")
                    return config
            except (json.JSONDecodeError, FileNotFoundError) as e:
                console.print(f"[yellow]⚠️  Error loading config: {e}. Using defaults.[/yellow]")
                return self.get_default_config()
        else:
            console.print(f"[blue]ℹ️  No config file found. Creating default configuration.[/blue]")
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "default_settings": {
                "output_format": "jpg",
                "resolution": "1024x1024",
                "aspect_ratio": "square",
                "quality": "high",
                "save_metadata": True,
                "auto_open_folder": False
            },
            "server_settings": {
                "host": "127.0.0.1",
                "port": 10000,
                "timeout": 120,
                "retry_attempts": 3
            },
            "ui_settings": {
                "show_progress": True,
                "show_timestamps": True,
                "color_theme": "default",
                "confirm_exit": True
            },
            "advanced_settings": {
                "fallback_enabled": True,
                "cache_images": True,
                "max_cache_size_mb": 500,
                "auto_cleanup_cache": True
            }
        }
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ Configuration saved to {self.config_file}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error saving config: {e}[/red]")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def update_section(self, section: str, updates: Dict[str, Any]) -> None:
        """Update entire configuration section"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section].update(updates)
        self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.get_default_config()
        self.save_config()
        console.print("[yellow]⚠️  Configuration reset to defaults[/yellow]")
    
    def show_config(self) -> None:
        """Display current configuration"""
        from rich.panel import Panel
        from rich.syntax import Syntax
        
        config_json = json.dumps(self.config, indent=2)
        syntax = Syntax(config_json, "json", theme="monokai", line_numbers=True)
        panel = Panel(syntax, title="Current Configuration", border_style="blue")
        console.print(panel)

# Global config instance
config = ConfigManager()

