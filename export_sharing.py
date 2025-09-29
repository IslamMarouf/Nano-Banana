#!/usr/bin/env python3
"""
Export options and social sharing system for Nano Banana Image Generator
"""

import json
import time
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import requests
from PIL import Image, ImageDraw, ImageFont
import io

console = Console()

@dataclass
class ExportFormat:
    """Data class for export formats"""
    name: str
    extension: str
    mime_type: str
    quality: int
    compression: str
    description: str

@dataclass
class SocialPlatform:
    """Data class for social media platforms"""
    name: str
    url: str
    max_file_size: int  # in MB
    supported_formats: List[str]
    aspect_ratios: List[str]
    description: str

class ExportManager:
    """Advanced export and sharing management system"""
    
    def __init__(self):
        self.export_formats = self._load_export_formats()
        self.social_platforms = self._load_social_platforms()
        self.export_history = []
        self.sharing_history = []
    
    def _load_export_formats(self) -> Dict[str, ExportFormat]:
        """Load available export formats"""
        return {
            "jpg": ExportFormat(
                name="JPEG",
                extension=".jpg",
                mime_type="image/jpeg",
                quality=95,
                compression="lossy",
                description="High quality JPEG with compression"
            ),
            "png": ExportFormat(
                name="PNG",
                extension=".png",
                mime_type="image/png",
                quality=100,
                compression="lossless",
                description="Lossless PNG with transparency support"
            ),
            "webp": ExportFormat(
                name="WebP",
                extension=".webp",
                mime_type="image/webp",
                quality=90,
                compression="lossy",
                description="Modern WebP format with excellent compression"
            ),
            "avif": ExportFormat(
                name="AVIF",
                extension=".avif",
                mime_type="image/avif",
                quality=90,
                compression="lossy",
                description="Next-gen AVIF format with superior compression"
            ),
            "tiff": ExportFormat(
                name="TIFF",
                extension=".tiff",
                mime_type="image/tiff",
                quality=100,
                compression="lossless",
                description="Professional TIFF format for printing"
            ),
            "bmp": ExportFormat(
                name="BMP",
                extension=".bmp",
                mime_type="image/bmp",
                quality=100,
                compression="lossless",
                description="Uncompressed bitmap format"
            ),
            "gif": ExportFormat(
                name="GIF",
                extension=".gif",
                mime_type="image/gif",
                quality=256,
                compression="lossless",
                description="Animated GIF format (static images supported)"
            )
        }
    
    def _load_social_platforms(self) -> Dict[str, SocialPlatform]:
        """Load social media platform configurations"""
        return {
            "instagram": SocialPlatform(
                name="Instagram",
                url="https://www.instagram.com/",
                max_file_size=30,
                supported_formats=["jpg", "png"],
                aspect_ratios=["1:1", "4:5", "16:9"],
                description="Photo and video sharing platform"
            ),
            "twitter": SocialPlatform(
                name="Twitter",
                url="https://twitter.com/",
                max_file_size=5,
                supported_formats=["jpg", "png", "gif"],
                aspect_ratios=["16:9", "1:1"],
                description="Microblogging and social media platform"
            ),
            "facebook": SocialPlatform(
                name="Facebook",
                url="https://www.facebook.com/",
                max_file_size=10,
                supported_formats=["jpg", "png", "gif"],
                aspect_ratios=["1:1", "16:9", "4:3"],
                description="Social networking platform"
            ),
            "pinterest": SocialPlatform(
                name="Pinterest",
                url="https://www.pinterest.com/",
                max_file_size=32,
                supported_formats=["jpg", "png", "gif"],
                aspect_ratios=["2:3", "1:1", "16:9"],
                description="Visual discovery and bookmarking platform"
            ),
            "linkedin": SocialPlatform(
                name="LinkedIn",
                url="https://www.linkedin.com/",
                max_file_size=5,
                supported_formats=["jpg", "png"],
                aspect_ratios=["1:1", "16:9"],
                description="Professional networking platform"
            ),
            "tumblr": SocialPlatform(
                name="Tumblr",
                url="https://www.tumblr.com/",
                max_file_size=10,
                supported_formats=["jpg", "png", "gif"],
                aspect_ratios=["16:9", "1:1", "3:4"],
                description="Microblogging and social media platform"
            ),
            "reddit": SocialPlatform(
                name="Reddit",
                url="https://www.reddit.com/",
                max_file_size=20,
                supported_formats=["jpg", "png", "gif"],
                aspect_ratios=["16:9", "1:1", "4:3"],
                description="Social news aggregation and discussion platform"
            ),
            "youtube": SocialPlatform(
                name="YouTube",
                url="https://www.youtube.com/",
                max_file_size=256,
                supported_formats=["jpg", "png"],
                aspect_ratios=["16:9"],
                description="Video sharing platform (for thumbnails)"
            )
        }
    
    def export_image(self, image_url: str, export_config: Dict[str, Any]) -> Dict[str, Any]:
        """Export image in specified format with optimizations"""
        format_name = export_config.get("format", "jpg")
        quality = export_config.get("quality", None)
        resize = export_config.get("resize", None)
        add_watermark = export_config.get("add_watermark", False)
        watermark_text = export_config.get("watermark_text", "Nano Banana")
        
        if format_name not in self.export_formats:
            return {"success": False, "error": f"Unsupported format: {format_name}"}
        
        format_info = self.export_formats[format_name]
        
        try:
            # Download original image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Open image with PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Apply optimizations
            if resize:
                image = self._resize_image(image, resize)
            
            if add_watermark:
                image = self._add_watermark(image, watermark_text)
            
            # Convert to specified format
            output = io.BytesIO()
            
            save_params = {}
            if format_info.compression == "lossy":
                save_params["quality"] = quality or format_info.quality
                save_params["optimize"] = True
            
            image.save(output, format=format_info.name.upper(), **save_params)
            
            # Prepare result
            result = {
                "success": True,
                "format": format_name,
                "mime_type": format_info.mime_type,
                "file_size": len(output.getvalue()),
                "dimensions": image.size,
                "optimizations": {
                    "resize": resize,
                    "watermark": add_watermark,
                    "quality": quality or format_info.quality
                }
            }
            
            # Save to file if requested
            if export_config.get("save_file"):
                filename = export_config.get("filename", f"export_{int(time.time())}{format_info.extension}")
                with open(filename, "wb") as f:
                    f.write(output.getvalue())
                result["filename"] = filename
            
            # Log export
            self._log_export(result)
            
            console.print(f"[green]✅ Exported as {format_name.upper()}[/green]")
            return result
            
        except Exception as e:
            console.print(f"[red]❌ Export error: {e}[/red]")
            return {"success": False, "error": str(e)}
    
    def _resize_image(self, image: Image.Image, resize_config: Dict[str, Any]) -> Image.Image:
        """Resize image according to configuration"""
        resize_type = resize_config.get("type", "fit")
        width = resize_config.get("width")
        height = resize_config.get("height")
        
        if not width and not height:
            return image
        
        if resize_type == "fit":
            # Maintain aspect ratio, fit within bounds
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
        elif resize_type == "fill":
            # Fill exact dimensions, may crop
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        elif resize_type == "stretch":
            # Stretch to exact dimensions
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        return image
    
    def _add_watermark(self, image: Image.Image, watermark_text: str) -> Image.Image:
        """Add watermark to image"""
        # Create a copy to avoid modifying original
        watermarked = image.copy()
        
        # Create drawing context
        draw = ImageDraw.Draw(watermarked)
        
        try:
            # Try to load a font
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate watermark position (bottom right)
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = watermarked.width - text_width - 10
        y = watermarked.height - text_height - 10
        
        # Draw watermark with semi-transparent background
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], fill=(0, 0, 0, 128))
        draw.text((x, y), watermark_text, fill=(255, 255, 255), font=font)
        
        return watermarked
    
    def optimize_for_platform(self, image_url: str, platform: str) -> Dict[str, Any]:
        """Optimize image for specific social media platform"""
        if platform not in self.social_platforms:
            return {"success": False, "error": f"Unknown platform: {platform}"}
        
        platform_info = self.social_platforms[platform]
        
        # Determine best format
        best_format = "jpg"  # Default
        for fmt in platform_info.supported_formats:
            if fmt in self.export_formats:
                best_format = fmt
                break
        
        # Determine optimal size (use first aspect ratio)
        aspect_ratio = platform_info.aspect_ratios[0] if platform_info.aspect_ratios else "1:1"
        width, height = self._calculate_dimensions_from_aspect_ratio(aspect_ratio, 1920)  # Max width
        
        # Ensure file size is within limits
        max_size_mb = platform_info.max_file_size
        quality = 95 if max_size_mb > 10 else 85 if max_size_mb > 5 else 75
        
        export_config = {
            "format": best_format,
            "quality": quality,
            "resize": {
                "type": "fit",
                "width": width,
                "height": height
            },
            "add_watermark": True,
            "watermark_text": "Created with Nano Banana"
        }
        
        return self.export_image(image_url, export_config)
    
    def _calculate_dimensions_from_aspect_ratio(self, aspect_ratio: str, max_width: int) -> Tuple[int, int]:
        """Calculate dimensions from aspect ratio"""
        if ":" in aspect_ratio:
            w_ratio, h_ratio = map(int, aspect_ratio.split(":"))
        else:
            # Handle decimal ratios like "1.77:1"
            w_ratio, h_ratio = map(float, aspect_ratio.split(":"))
            w_ratio, h_ratio = int(w_ratio * 100), int(h_ratio * 100)
        
        width = min(max_width, 4096)  # Cap at 4K
        height = int(width * h_ratio / w_ratio)
        
        return width, height
    
    def batch_export(self, image_urls: List[str], export_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export multiple images with different configurations"""
        results = {
            "total_images": len(image_urls),
            "successful_exports": 0,
            "failed_exports": 0,
            "export_results": []
        }
        
        console.print(f"[cyan]📤 Batch exporting {len(image_urls)} images[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Exporting images...", total=len(image_urls))
            
            for i, image_url in enumerate(image_urls):
                config = export_configs[i] if i < len(export_configs) else export_configs[0]
                
                result = self.export_image(image_url, config)
                results["export_results"].append(result)
                
                if result["success"]:
                    results["successful_exports"] += 1
                else:
                    results["failed_exports"] += 1
                
                progress.update(task, advance=1, description=f"Exported {i+1}/{len(image_urls)}")
        
        return results
    
    def generate_sharing_links(self, image_url: str, platforms: List[str]) -> Dict[str, str]:
        """Generate sharing links for social media platforms"""
        sharing_links = {}
        
        for platform in platforms:
            if platform == "twitter":
                text = "Check out this AI-generated image created with Nano Banana!"
                sharing_links["twitter"] = f"https://twitter.com/intent/tweet?text={text}&url={image_url}"
            elif platform == "facebook":
                sharing_links["facebook"] = f"https://www.facebook.com/sharer/sharer.php?u={image_url}"
            elif platform == "linkedin":
                text = "AI-generated image created with Nano Banana"
                sharing_links["linkedin"] = f"https://www.linkedin.com/sharing/share-offsite/?url={image_url}&summary={text}"
            elif platform == "pinterest":
                text = "AI-generated image"
                sharing_links["pinterest"] = f"https://pinterest.com/pin/create/button/?url={image_url}&description={text}"
            elif platform == "reddit":
                text = "AI-generated image created with Nano Banana"
                sharing_links["reddit"] = f"https://reddit.com/submit?url={image_url}&title={text}"
        
        return sharing_links
    
    def _log_export(self, export_result: Dict[str, Any]):
        """Log export operation"""
        log_entry = {
            "timestamp": time.time(),
            "format": export_result.get("format"),
            "file_size": export_result.get("file_size"),
            "dimensions": export_result.get("dimensions"),
            "optimizations": export_result.get("optimizations")
        }
        
        self.export_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.export_history) > 1000:
            self.export_history = self.export_history[-1000:]
    
    def display_export_formats(self):
        """Display available export formats"""
        console.print("\n[bold cyan]📁 Available Export Formats[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Format", style="cyan", width=8)
        table.add_column("Extension", style="green", width=10)
        table.add_column("Compression", style="yellow", width=12)
        table.add_column("Quality", style="blue", width=8)
        table.add_column("Description", style="white", width=40)
        
        for format_name, format_info in self.export_formats.items():
            table.add_row(
                format_name.upper(),
                format_info.extension,
                format_info.compression.title(),
                str(format_info.quality),
                format_info.description
            )
        
        console.print(table)
    
    def display_social_platforms(self):
        """Display available social media platforms"""
        console.print("\n[bold cyan]📱 Supported Social Platforms[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Platform", style="cyan", width=12)
        table.add_column("Max Size", style="green", width=10)
        table.add_column("Formats", style="yellow", width=15)
        table.add_column("Aspect Ratios", style="blue", width=20)
        table.add_column("Description", style="white", width=30)
        
        for platform_name, platform_info in self.social_platforms.items():
            table.add_row(
                platform_info.name,
                f"{platform_info.max_file_size}MB",
                ", ".join(platform_info.supported_formats),
                ", ".join(platform_info.aspect_ratios[:3]),  # Show first 3
                platform_info.description
            )
        
        console.print(table)
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export statistics"""
        total_exports = len(self.export_history)
        
        format_counts = {}
        total_size = 0
        
        for export in self.export_history:
            format_name = export.get("format", "unknown")
            format_counts[format_name] = format_counts.get(format_name, 0) + 1
            total_size += export.get("file_size", 0)
        
        return {
            "total_exports": total_exports,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "format_counts": format_counts,
            "average_size_mb": round(total_size / (1024 * 1024) / total_exports, 2) if total_exports > 0 else 0
        }

def demo_export_and_sharing():
    """Demo export and sharing features"""
    banner = Panel(
        "[bold blue]📤 Export & Sharing Demo[/bold blue]\n\n"
        "Demonstrating advanced export options and social media integration",
        title="Export & Sharing",
        border_style="blue"
    )
    console.print(banner)
    
    export_manager = ExportManager()
    
    # Display available formats and platforms
    export_manager.display_export_formats()
    export_manager.display_social_platforms()
    
    # Demo export configurations
    console.print("\n[bold cyan]🎨 Export Configuration Demo[/bold cyan]")
    
    demo_image_url = "https://example.com/demo_image.jpg"
    
    # Different export configurations
    export_configs = [
        {
            "format": "png",
            "quality": 100,
            "add_watermark": True,
            "watermark_text": "Nano Banana AI"
        },
        {
            "format": "webp",
            "quality": 90,
            "resize": {"type": "fit", "width": 1920, "height": 1080},
            "add_watermark": False
        },
        {
            "format": "jpg",
            "quality": 85,
            "resize": {"type": "fill", "width": 1024, "height": 1024},
            "add_watermark": True,
            "watermark_text": "AI Generated"
        }
    ]
    
    console.print("\n[bold yellow]Export Configurations:[/bold yellow]")
    for i, config in enumerate(export_configs, 1):
        console.print(f"  {i}. {config['format'].upper()} - Quality: {config['quality']} - Watermark: {config['add_watermark']}")
    
    # Demo platform optimization
    console.print("\n[bold cyan]📱 Platform Optimization Demo[/bold cyan]")
    
    platforms_to_demo = ["instagram", "twitter", "pinterest", "linkedin"]
    
    for platform in platforms_to_demo:
        console.print(f"\n[bold yellow]Optimizing for {platform.title()}:[/bold yellow]")
        result = export_manager.optimize_for_platform(demo_image_url, platform)
        if result["success"]:
            console.print(f"  ✅ Format: {result['format']}")
            console.print(f"  📏 Size: {result['file_size']} bytes")
            console.print(f"  🖼️ Dimensions: {result['dimensions']}")
        else:
            console.print(f"  ❌ Error: {result['error']}")
    
    # Demo sharing links
    console.print("\n[bold cyan]🔗 Sharing Links Demo[/bold cyan]")
    
    sharing_links = export_manager.generate_sharing_links(demo_image_url, platforms_to_demo)
    
    for platform, link in sharing_links.items():
        console.print(f"  {platform.title()}: {link[:80]}...")
    
    # Demo batch export
    console.print("\n[bold cyan]📦 Batch Export Demo[/bold cyan]")
    
    batch_result = export_manager.batch_export([demo_image_url], export_configs)
    
    console.print(f"Total Images: {batch_result['total_images']}")
    console.print(f"Successful: {batch_result['successful_exports']}")
    console.print(f"Failed: {batch_result['failed_exports']}")
    
    # Show statistics
    stats = export_manager.get_export_statistics()
    
    stats_panel = Panel(
        f"[bold blue]📊 Export Statistics[/bold blue]\n\n"
        f"Total Exports: {stats['total_exports']}\n"
        f"Total Size: {stats['total_size_mb']} MB\n"
        f"Average Size: {stats['average_size_mb']} MB\n\n"
        f"[bold]Format Distribution:[/bold]\n" +
        "\n".join([f"• {fmt}: {count}" for fmt, count in stats['format_counts'].items()]),
        title="Export Stats",
        border_style="blue"
    )
    console.print(stats_panel)
    
    # Feature summary
    features_panel = Panel(
        "[bold green]🎉 Export & Sharing Features:[/bold green]\n\n"
        "✅ Multiple export formats (JPEG, PNG, WebP, AVIF, TIFF, BMP, GIF)\n"
        "✅ Quality and compression optimization\n"
        "✅ Automatic resizing and aspect ratio adjustment\n"
        "✅ Watermarking capabilities\n"
        "✅ Platform-specific optimization\n"
        "✅ Social media sharing links\n"
        "✅ Batch export processing\n"
        "✅ Export statistics and analytics\n"
        "✅ File size optimization\n"
        "✅ Professional printing formats\n"
        "✅ Web-optimized formats\n\n"
        "[bold yellow]💡 Export your images in any format for any platform![/bold yellow]",
        title="Export & Sharing Complete",
        border_style="green"
    )
    console.print(features_panel)

def main():
    """Main function for export and sharing demo"""
    demo_export_and_sharing()

if __name__ == "__main__":
    main()
