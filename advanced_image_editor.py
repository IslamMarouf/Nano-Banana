#!/usr/bin/env python3
"""
Advanced image editing system for Nano Banana Image Generator
"""

import json
import time
import base64
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io

console = Console()

@dataclass
class EditOperation:
    """Data class for edit operations"""
    type: str  # "inpaint", "outpaint", "style_transfer", "color_adjust", "filter"
    parameters: Dict[str, Any]
    description: str
    confidence: float

class AdvancedImageEditor:
    """Advanced image editing system with AI-powered features"""
    
    def __init__(self, api_base: str = "http://127.0.0.1:10000"):
        self.api_base = api_base
        self.edit_history = []
        self.style_presets = self._load_style_presets()
        self.filter_presets = self._load_filter_presets()
    
    def _load_style_presets(self) -> Dict[str, Dict[str, Any]]:
        """Load style transfer presets"""
        return {
            "van_gogh": {
                "prompt": "in the style of Vincent van Gogh, post-impressionist, swirling brushstrokes, vibrant colors",
                "description": "Van Gogh's post-impressionist style"
            },
            "picasso": {
                "prompt": "in the style of Pablo Picasso, cubist, abstract, geometric forms",
                "description": "Picasso's cubist style"
            },
            "monet": {
                "prompt": "in the style of Claude Monet, impressionist, soft brushstrokes, natural lighting",
                "description": "Monet's impressionist style"
            },
            "anime": {
                "prompt": "anime style, manga, japanese animation, cel shading, vibrant colors",
                "description": "Anime/manga style"
            },
            "photorealistic": {
                "prompt": "photorealistic, hyperrealistic, detailed, sharp focus, professional photography",
                "description": "Photorealistic style"
            },
            "watercolor": {
                "prompt": "watercolor painting, soft colors, flowing, artistic, traditional painting",
                "description": "Watercolor painting style"
            },
            "oil_painting": {
                "prompt": "oil painting, classical art, rich colors, brushstrokes, traditional painting",
                "description": "Classical oil painting style"
            },
            "digital_art": {
                "prompt": "digital art, concept art, modern illustration, vibrant, detailed",
                "description": "Modern digital art style"
            },
            "sketch": {
                "prompt": "pencil sketch, line art, drawing, monochrome, artistic",
                "description": "Pencil sketch style"
            },
            "vintage": {
                "prompt": "vintage style, retro, aged, sepia tones, classic photography",
                "description": "Vintage/retro style"
            }
        }
    
    def _load_filter_presets(self) -> Dict[str, Dict[str, Any]]:
        """Load image filter presets"""
        return {
            "blur": {
                "type": "blur",
                "parameters": {"radius": 5},
                "description": "Soft blur effect"
            },
            "sharpen": {
                "type": "sharpen",
                "parameters": {},
                "description": "Enhance image sharpness"
            },
            "emboss": {
                "type": "emboss",
                "parameters": {},
                "description": "Embossed effect"
            },
            "edge_enhance": {
                "type": "edge_enhance",
                "parameters": {},
                "description": "Enhance edges"
            },
            "smooth": {
                "type": "smooth",
                "parameters": {},
                "description": "Smooth image"
            },
            "contour": {
                "type": "contour",
                "parameters": {},
                "description": "Contour effect"
            },
            "detail": {
                "type": "detail",
                "parameters": {},
                "description": "Enhance details"
            }
        }
    
    def inpaint_image(self, image_url: str, mask_description: str, replacement_prompt: str) -> Dict[str, Any]:
        """Remove objects and replace them with new content"""
        console.print(f"[cyan]🎨 Inpainting: {mask_description} → {replacement_prompt}[/cyan]")
        
        # Create inpaint prompt
        inpaint_prompt = f"Remove {mask_description} and replace with {replacement_prompt}, seamless integration, natural looking"
        
        try:
            response = requests.post(
                f"{self.api_base}/v1/image/generations",
                json={
                    "prompt": inpaint_prompt,
                    "image_url": image_url,
                    "type": "inpaint"
                },
                timeout=120
            )
            
            if response.ok:
                data = response.json()
                result_url = data["data"][0]["url"]
                
                operation = EditOperation(
                    type="inpaint",
                    parameters={
                        "mask_description": mask_description,
                        "replacement_prompt": replacement_prompt,
                        "original_url": image_url
                    },
                    description=f"Inpainted: {mask_description} → {replacement_prompt}",
                    confidence=0.85
                )
                
                self.edit_history.append(operation)
                
                return {
                    "success": True,
                    "result_url": result_url,
                    "operation": operation
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def outpaint_image(self, image_url: str, expansion_direction: str, expansion_prompt: str) -> Dict[str, Any]:
        """Extend image beyond its original boundaries"""
        console.print(f"[cyan]🖼️ Outpainting: Expanding {expansion_direction} with {expansion_prompt}[/cyan]")
        
        # Create outpaint prompt
        outpaint_prompt = f"Extend the image to the {expansion_direction} with {expansion_prompt}, seamless continuation, natural extension"
        
        try:
            response = requests.post(
                f"{self.api_base}/v1/image/generations",
                json={
                    "prompt": outpaint_prompt,
                    "image_url": image_url,
                    "type": "outpaint",
                    "direction": expansion_direction
                },
                timeout=120
            )
            
            if response.ok:
                data = response.json()
                result_url = data["data"][0]["url"]
                
                operation = EditOperation(
                    type="outpaint",
                    parameters={
                        "direction": expansion_direction,
                        "expansion_prompt": expansion_prompt,
                        "original_url": image_url
                    },
                    description=f"Outpainted {expansion_direction}: {expansion_prompt}",
                    confidence=0.80
                )
                
                self.edit_history.append(operation)
                
                return {
                    "success": True,
                    "result_url": result_url,
                    "operation": operation
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def style_transfer(self, image_url: str, style_preset: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Apply artistic style to an image"""
        style_info = self.style_presets.get(style_preset)
        if not style_info:
            return {"success": False, "error": f"Unknown style preset: {style_preset}"}
        
        style_prompt = custom_prompt or style_info["prompt"]
        console.print(f"[cyan]🎭 Style Transfer: {style_info['description']}[/cyan]")
        
        try:
            response = requests.post(
                f"{self.api_base}/v1/image/generations",
                json={
                    "prompt": f"Transform this image {style_prompt}, maintain composition and subject",
                    "image_url": image_url,
                    "type": "style_transfer"
                },
                timeout=120
            )
            
            if response.ok:
                data = response.json()
                result_url = data["data"][0]["url"]
                
                operation = EditOperation(
                    type="style_transfer",
                    parameters={
                        "style_preset": style_preset,
                        "style_prompt": style_prompt,
                        "original_url": image_url
                    },
                    description=f"Style transfer: {style_info['description']}",
                    confidence=0.90
                )
                
                self.edit_history.append(operation)
                
                return {
                    "success": True,
                    "result_url": result_url,
                    "operation": operation
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def color_adjustment(self, image_url: str, adjustment_type: str, intensity: float = 0.5) -> Dict[str, Any]:
        """Adjust colors of an image"""
        console.print(f"[cyan]🎨 Color Adjustment: {adjustment_type} (intensity: {intensity})[/cyan]")
        
        adjustment_prompts = {
            "brightness": f"increase brightness by {intensity * 100:.0f}%",
            "contrast": f"increase contrast by {intensity * 100:.0f}%",
            "saturation": f"increase color saturation by {intensity * 100:.0f}%",
            "warmth": f"add warm tones, golden hour lighting",
            "coolness": f"add cool tones, blue hour lighting",
            "vintage": f"apply vintage color grading, sepia tones",
            "high_contrast": "apply high contrast, dramatic lighting",
            "pastel": "apply pastel color palette, soft colors"
        }
        
        adjustment_prompt = adjustment_prompts.get(adjustment_type, f"apply {adjustment_type} adjustment")
        
        try:
            response = requests.post(
                f"{self.api_base}/v1/image/generations",
                json={
                    "prompt": f"Adjust colors: {adjustment_prompt}",
                    "image_url": image_url,
                    "type": "color_adjustment"
                },
                timeout=120
            )
            
            if response.ok:
                data = response.json()
                result_url = data["data"][0]["url"]
                
                operation = EditOperation(
                    type="color_adjust",
                    parameters={
                        "adjustment_type": adjustment_type,
                        "intensity": intensity,
                        "original_url": image_url
                    },
                    description=f"Color adjustment: {adjustment_type}",
                    confidence=0.75
                )
                
                self.edit_history.append(operation)
                
                return {
                    "success": True,
                    "result_url": result_url,
                    "operation": operation
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def apply_filter(self, image_url: str, filter_preset: str) -> Dict[str, Any]:
        """Apply image filters"""
        filter_info = self.filter_presets.get(filter_preset)
        if not filter_info:
            return {"success": False, "error": f"Unknown filter preset: {filter_preset}"}
        
        console.print(f"[cyan]🔧 Applying Filter: {filter_info['description']}[/cyan]")
        
        filter_prompts = {
            "blur": "apply soft blur effect, dreamy atmosphere",
            "sharpen": "enhance sharpness, crisp details",
            "emboss": "apply embossed effect, raised appearance",
            "edge_enhance": "enhance edges, define boundaries",
            "smooth": "apply smoothing, soft appearance",
            "contour": "apply contour effect, outlined appearance",
            "detail": "enhance fine details, texture"
        }
        
        filter_prompt = filter_prompts.get(filter_preset, f"apply {filter_preset} filter")
        
        try:
            response = requests.post(
                f"{self.api_base}/v1/image/generations",
                json={
                    "prompt": f"Apply filter: {filter_prompt}",
                    "image_url": image_url,
                    "type": "filter"
                },
                timeout=120
            )
            
            if response.ok:
                data = response.json()
                result_url = data["data"][0]["url"]
                
                operation = EditOperation(
                    type="filter",
                    parameters={
                        "filter_preset": filter_preset,
                        "original_url": image_url
                    },
                    description=f"Filter: {filter_info['description']}",
                    confidence=0.70
                )
                
                self.edit_history.append(operation)
                
                return {
                    "success": True,
                    "result_url": result_url,
                    "operation": operation
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def batch_edit(self, image_url: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply multiple edits in sequence"""
        console.print(f"[cyan]🔄 Batch Editing: {len(operations)} operations[/cyan]")
        
        results = []
        current_url = image_url
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing batch edits...", total=len(operations))
            
            for i, operation in enumerate(operations):
                progress.update(task, advance=1, description=f"Processing operation {i+1}/{len(operations)}")
                
                op_type = operation.get("type")
                
                if op_type == "style_transfer":
                    result = self.style_transfer(
                        current_url,
                        operation.get("style_preset"),
                        operation.get("custom_prompt")
                    )
                elif op_type == "color_adjust":
                    result = self.color_adjustment(
                        current_url,
                        operation.get("adjustment_type"),
                        operation.get("intensity", 0.5)
                    )
                elif op_type == "filter":
                    result = self.apply_filter(
                        current_url,
                        operation.get("filter_preset")
                    )
                else:
                    result = {"success": False, "error": f"Unknown operation type: {op_type}"}
                
                results.append(result)
                
                if result["success"]:
                    current_url = result["result_url"]
                else:
                    console.print(f"[red]❌ Operation {i+1} failed: {result['error']}[/red]")
                    break
        
        return {
            "success": len([r for r in results if r["success"]]) == len(operations),
            "results": results,
            "final_url": current_url if results and results[-1]["success"] else image_url
        }
    
    def get_edit_history(self) -> List[EditOperation]:
        """Get edit history"""
        return self.edit_history
    
    def display_style_presets(self):
        """Display available style presets"""
        console.print("\n[bold cyan]🎭 Available Style Presets[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Style", style="cyan", width=15)
        table.add_column("Description", style="green", width=40)
        table.add_column("Prompt", style="yellow", width=50)
        
        for style_name, style_info in self.style_presets.items():
            table.add_row(
                style_name.replace("_", " ").title(),
                style_info["description"],
                style_info["prompt"][:50] + "..." if len(style_info["prompt"]) > 50 else style_info["prompt"]
            )
        
        console.print(table)
    
    def display_filter_presets(self):
        """Display available filter presets"""
        console.print("\n[bold cyan]🔧 Available Filter Presets[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Filter", style="cyan", width=15)
        table.add_column("Description", style="green", width=30)
        table.add_column("Type", style="yellow", width=15)
        
        for filter_name, filter_info in self.filter_presets.items():
            table.add_row(
                filter_name.replace("_", " ").title(),
                filter_info["description"],
                filter_info["type"]
            )
        
        console.print(table)

def demo_advanced_editing():
    """Demo advanced image editing features"""
    banner = Panel(
        "[bold blue]🎨 Advanced Image Editor Demo[/bold blue]\n\n"
        "Demonstrating AI-powered image editing capabilities",
        title="Advanced Editing",
        border_style="blue"
    )
    console.print(banner)
    
    editor = AdvancedImageEditor()
    
    # Display available presets
    editor.display_style_presets()
    editor.display_filter_presets()
    
    # Demo operations (these would normally work with real images)
    console.print("\n[bold cyan]🔄 Demo Operations[/bold cyan]")
    
    demo_image_url = "https://example.com/demo_image.jpg"
    
    # Style transfer demo
    console.print("\n[bold yellow]1. Style Transfer Demo[/bold yellow]")
    style_result = editor.style_transfer(demo_image_url, "van_gogh")
    if style_result["success"]:
        console.print("✅ Style transfer completed")
    else:
        console.print(f"❌ Style transfer failed: {style_result['error']}")
    
    # Color adjustment demo
    console.print("\n[bold yellow]2. Color Adjustment Demo[/bold yellow]")
    color_result = editor.color_adjustment(demo_image_url, "warmth", 0.7)
    if color_result["success"]:
        console.print("✅ Color adjustment completed")
    else:
        console.print(f"❌ Color adjustment failed: {color_result['error']}")
    
    # Batch editing demo
    console.print("\n[bold yellow]3. Batch Editing Demo[/bold yellow]")
    batch_operations = [
        {"type": "style_transfer", "style_preset": "anime"},
        {"type": "color_adjust", "adjustment_type": "saturation", "intensity": 0.8},
        {"type": "filter", "filter_preset": "sharpen"}
    ]
    
    batch_result = editor.batch_edit(demo_image_url, batch_operations)
    if batch_result["success"]:
        console.print("✅ Batch editing completed")
    else:
        console.print("❌ Batch editing failed")
    
    # Show edit history
    history = editor.get_edit_history()
    if history:
        console.print(f"\n[bold cyan]📚 Edit History: {len(history)} operations[/bold cyan]")
        
        history_table = Table(show_header=True, header_style="bold magenta")
        history_table.add_column("Type", style="cyan", width=15)
        history_table.add_column("Description", style="green", width=40)
        history_table.add_column("Confidence", style="yellow", width=12)
        
        for operation in history:
            history_table.add_row(
                operation.type.replace("_", " ").title(),
                operation.description,
                f"{operation.confidence:.2f}"
            )
        
        console.print(history_table)
    
    # Feature summary
    features_panel = Panel(
        "[bold green]🎉 Advanced Image Editor Features:[/bold green]\n\n"
        "✅ AI-powered inpainting (remove/replace objects)\n"
        "✅ Intelligent outpainting (extend boundaries)\n"
        "✅ Style transfer with 10+ artistic presets\n"
        "✅ Color adjustment and grading\n"
        "✅ Image filters and effects\n"
        "✅ Batch editing operations\n"
        "✅ Edit history tracking\n"
        "✅ Confidence scoring\n"
        "✅ Seamless integration with generation API\n\n"
        "[bold yellow]💡 Transform your images with AI-powered editing![/bold yellow]",
        title="Advanced Editor Complete",
        border_style="green"
    )
    console.print(features_panel)

def main():
    """Main function for advanced image editor"""
    demo_advanced_editing()

if __name__ == "__main__":
    main()
