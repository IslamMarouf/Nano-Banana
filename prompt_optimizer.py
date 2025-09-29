#!/usr/bin/env python3
"""
AI-powered prompt optimization system for Nano Banana Image Generator
"""

import re
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class PromptSuggestion:
    """Data class for prompt suggestions"""
    type: str  # "style", "quality", "composition", "lighting", "subject"
    suggestion: str
    confidence: float
    reason: str

class PromptOptimizer:
    """AI-powered prompt optimization system"""
    
    def __init__(self):
        self.style_keywords = {
            "photorealistic": ["realistic", "photo", "detailed", "sharp", "high resolution"],
            "artistic": ["artistic", "painting", "artwork", "creative", "expressive"],
            "anime": ["anime", "manga", "japanese", "kawaii", "chibi"],
            "digital_art": ["digital art", "concept art", "illustration", "digital painting"],
            "oil_painting": ["oil painting", "brushstrokes", "classical", "traditional"],
            "watercolor": ["watercolor", "soft", "flowing", "gentle", "delicate"],
            "sketch": ["sketch", "drawing", "pencil", "charcoal", "line art"],
            "3d_render": ["3d render", "blender", "maya", "cinema4d", "3d model"],
            "vintage": ["vintage", "retro", "old", "classic", "antique"],
            "futuristic": ["futuristic", "sci-fi", "cyberpunk", "high-tech", "modern"]
        }
        
        self.quality_enhancers = [
            "high quality", "detailed", "sharp focus", "professional",
            "masterpiece", "award winning", "cinematic", "4k", "8k",
            "ultra detailed", "perfect", "flawless", "stunning"
        ]
        
        self.composition_terms = [
            "rule of thirds", "golden ratio", "symmetrical", "asymmetrical",
            "leading lines", "depth of field", "shallow focus", "wide angle",
            "close up", "macro", "panoramic", "bird's eye view", "low angle"
        ]
        
        self.lighting_terms = [
            "natural lighting", "golden hour", "blue hour", "dramatic lighting",
            "soft lighting", "harsh lighting", "rim lighting", "backlighting",
            "side lighting", "studio lighting", "ambient lighting", "moody lighting"
        ]
        
        self.negative_prompts = [
            "blurry", "low quality", "pixelated", "grainy", "noisy",
            "distorted", "deformed", "ugly", "bad anatomy", "extra limbs",
            "missing limbs", "bad proportions", "watermark", "text", "signature"
        ]
        
        self.subject_categories = {
            "people": ["person", "man", "woman", "child", "baby", "portrait", "face"],
            "animals": ["cat", "dog", "bird", "horse", "lion", "tiger", "elephant"],
            "nature": ["landscape", "mountain", "forest", "ocean", "lake", "sunset", "sunrise"],
            "architecture": ["building", "house", "castle", "bridge", "tower", "skyscraper"],
            "objects": ["car", "flower", "food", "book", "computer", "phone", "furniture"],
            "abstract": ["pattern", "texture", "color", "shape", "form", "design"]
        }
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze a prompt and provide optimization suggestions"""
        analysis = {
            "original": prompt,
            "word_count": len(prompt.split()),
            "has_style": False,
            "has_quality": False,
            "has_lighting": False,
            "has_composition": False,
            "suggestions": [],
            "confidence": 0.0
        }
        
        prompt_lower = prompt.lower()
        
        # Check for existing elements
        for style in self.style_keywords:
            if any(keyword in prompt_lower for keyword in self.style_keywords[style]):
                analysis["has_style"] = True
                break
        
        analysis["has_quality"] = any(term in prompt_lower for term in self.quality_enhancers)
        analysis["has_lighting"] = any(term in prompt_lower for term in self.lighting_terms)
        analysis["has_composition"] = any(term in prompt_lower for term in self.composition_terms)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(prompt_lower, analysis)
        analysis["suggestions"] = suggestions
        
        # Calculate confidence score
        analysis["confidence"] = self._calculate_confidence(analysis)
        
        return analysis
    
    def _generate_suggestions(self, prompt: str, analysis: Dict[str, Any]) -> List[PromptSuggestion]:
        """Generate optimization suggestions for the prompt"""
        suggestions = []
        
        # Style suggestions
        if not analysis["has_style"]:
            detected_subject = self._detect_subject_category(prompt)
            if detected_subject:
                style_suggestion = self._get_style_suggestion(detected_subject)
                suggestions.append(PromptSuggestion(
                    type="style",
                    suggestion=style_suggestion,
                    confidence=0.8,
                    reason=f"Detected {detected_subject} subject - adding appropriate style"
                ))
        
        # Quality enhancement suggestions
        if not analysis["has_quality"]:
            suggestions.append(PromptSuggestion(
                type="quality",
                suggestion="high quality, detailed",
                confidence=0.9,
                reason="Adding quality enhancers for better results"
            ))
        
        # Lighting suggestions
        if not analysis["has_lighting"]:
            suggestions.append(PromptSuggestion(
                type="lighting",
                suggestion="natural lighting",
                confidence=0.7,
                reason="Adding lighting specification for better visual appeal"
            ))
        
        # Composition suggestions
        if not analysis["has_composition"]:
            suggestions.append(PromptSuggestion(
                type="composition",
                suggestion="rule of thirds",
                confidence=0.6,
                reason="Adding composition guidance for better framing"
            ))
        
        return suggestions
    
    def _detect_subject_category(self, prompt: str) -> Optional[str]:
        """Detect the main subject category of the prompt"""
        for category, keywords in self.subject_categories.items():
            if any(keyword in prompt for keyword in keywords):
                return category
        return None
    
    def _get_style_suggestion(self, subject_category: str) -> str:
        """Get appropriate style suggestion based on subject category"""
        style_mapping = {
            "people": "portrait photography, professional",
            "animals": "wildlife photography, detailed",
            "nature": "landscape photography, scenic",
            "architecture": "architectural photography, modern",
            "objects": "product photography, studio",
            "abstract": "abstract art, creative"
        }
        return style_mapping.get(subject_category, "artistic, detailed")
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        score = 0.0
        max_score = 4.0
        
        if analysis["has_style"]:
            score += 1.0
        if analysis["has_quality"]:
            score += 1.0
        if analysis["has_lighting"]:
            score += 1.0
        if analysis["has_composition"]:
            score += 1.0
        
        return score / max_score
    
    def optimize_prompt(self, prompt: str, apply_all: bool = False) -> str:
        """Generate an optimized version of the prompt"""
        analysis = self.analyze_prompt(prompt)
        optimized_parts = [prompt]
        
        for suggestion in analysis["suggestions"]:
            if apply_all or suggestion.confidence > 0.7:
                optimized_parts.append(suggestion.suggestion)
        
        return ", ".join(optimized_parts)
    
    def get_style_variations(self, prompt: str, num_variations: int = 3) -> List[str]:
        """Generate style variations of a prompt"""
        base_prompt = self._remove_style_keywords(prompt)
        variations = []
        
        # Get popular styles
        popular_styles = ["photorealistic", "artistic", "anime", "digital_art", "oil_painting"]
        
        for i, style in enumerate(popular_styles[:num_variations]):
            style_keywords = self.style_keywords[style]
            style_term = style_keywords[0]  # Use the first keyword
            variation = f"{style_term}, {base_prompt}"
            variations.append(variation)
        
        return variations
    
    def _remove_style_keywords(self, prompt: str) -> str:
        """Remove existing style keywords from prompt"""
        prompt_lower = prompt.lower()
        cleaned_prompt = prompt
        
        for style_keywords in self.style_keywords.values():
            for keyword in style_keywords:
                if keyword in prompt_lower:
                    # Remove the keyword and surrounding commas
                    pattern = rf"\b{re.escape(keyword)}\b,?\s*"
                    cleaned_prompt = re.sub(pattern, "", cleaned_prompt, flags=re.IGNORECASE)
        
        return cleaned_prompt.strip(", ")
    
    def get_negative_prompts(self, prompt: str) -> List[str]:
        """Generate negative prompts to avoid unwanted elements"""
        prompt_lower = prompt.lower()
        negative_prompts = []
        
        # Add general negative prompts
        negative_prompts.extend(self.negative_prompts[:5])
        
        # Add specific negative prompts based on content
        if "person" in prompt_lower or "man" in prompt_lower or "woman" in prompt_lower:
            negative_prompts.extend(["bad anatomy", "extra limbs", "missing limbs"])
        
        if "animal" in prompt_lower or "pet" in prompt_lower:
            negative_prompts.extend(["deformed", "mutated", "extra heads"])
        
        return negative_prompts[:8]  # Limit to 8 negative prompts
    
    def analyze_prompt_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze the complexity of a prompt"""
        words = prompt.split()
        
        complexity_analysis = {
            "word_count": len(words),
            "complexity_level": "simple",
            "readability_score": 0.0,
            "technical_terms": 0,
            "artistic_terms": 0,
            "suggestions": []
        }
        
        # Count technical and artistic terms
        technical_terms = ["camera", "lens", "aperture", "shutter", "iso", "exposure", "focal"]
        artistic_terms = ["style", "mood", "atmosphere", "emotion", "feeling", "expression"]
        
        for word in words:
            if any(term in word.lower() for term in technical_terms):
                complexity_analysis["technical_terms"] += 1
            if any(term in word.lower() for term in artistic_terms):
                complexity_analysis["artistic_terms"] += 1
        
        # Determine complexity level
        if len(words) < 10:
            complexity_analysis["complexity_level"] = "simple"
        elif len(words) < 20:
            complexity_analysis["complexity_level"] = "medium"
        else:
            complexity_analysis["complexity_level"] = "complex"
        
        # Calculate readability score (simplified)
        complexity_analysis["readability_score"] = min(1.0, len(words) / 30.0)
        
        # Generate suggestions based on complexity
        if complexity_analysis["complexity_level"] == "simple":
            complexity_analysis["suggestions"].append("Consider adding more descriptive details")
        elif complexity_analysis["complexity_level"] == "complex":
            complexity_analysis["suggestions"].append("Consider simplifying for better focus")
        
        return complexity_analysis

def display_prompt_analysis(analysis: Dict[str, Any]):
    """Display prompt analysis in a nice format"""
    console.print("\n[bold cyan]📝 Prompt Analysis Results[/bold cyan]")
    
    # Summary panel
    summary_panel = Panel(
        f"[bold]Original Prompt:[/bold] {analysis['original']}\n"
        f"[bold]Word Count:[/bold] {analysis['word_count']}\n"
        f"[bold]Confidence Score:[/bold] {analysis['confidence']:.2f}/1.0\n"
        f"[bold]Has Style:[/bold] {'✅' if analysis['has_style'] else '❌'}\n"
        f"[bold]Has Quality:[/bold] {'✅' if analysis['has_quality'] else '❌'}\n"
        f"[bold]Has Lighting:[/bold] {'✅' if analysis['has_lighting'] else '❌'}\n"
        f"[bold]Has Composition:[/bold] {'✅' if analysis['has_composition'] else '❌'}",
        title="Analysis Summary",
        border_style="blue"
    )
    console.print(summary_panel)
    
    # Suggestions table
    if analysis['suggestions']:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Suggestion", style="green", width=40)
        table.add_column("Confidence", style="yellow", width=10)
        table.add_column("Reason", style="blue", width=30)
        
        for suggestion in analysis['suggestions']:
            table.add_row(
                suggestion.type.title(),
                suggestion.suggestion,
                f"{suggestion.confidence:.2f}",
                suggestion.reason
            )
        
        console.print(table)

def main():
    """Main function for prompt optimization demo"""
    banner = Panel(
        "[bold blue]🤖 AI Prompt Optimizer[/bold blue]\n\n"
        "Intelligent prompt analysis and optimization for better image generation",
        title="Prompt Optimization",
        border_style="blue"
    )
    console.print(banner)
    
    optimizer = PromptOptimizer()
    
    # Demo prompts
    demo_prompts = [
        "a cat",
        "beautiful sunset over mountains with trees",
        "portrait of a woman",
        "futuristic city with flying cars and neon lights, cinematic lighting, high quality, detailed",
        "abstract art with colors"
    ]
    
    console.print("\n[bold cyan]🔍 Analyzing Demo Prompts[/bold cyan]")
    
    for i, prompt in enumerate(demo_prompts, 1):
        console.print(f"\n[bold yellow]Prompt {i}:[/bold yellow] {prompt}")
        
        # Analyze prompt
        analysis = optimizer.analyze_prompt(prompt)
        display_prompt_analysis(analysis)
        
        # Show optimized version
        optimized = optimizer.optimize_prompt(prompt, apply_all=True)
        console.print(f"\n[bold green]✨ Optimized:[/bold green] {optimized}")
        
        # Show style variations
        variations = optimizer.get_style_variations(prompt, 3)
        console.print("\n[bold magenta]🎨 Style Variations:[/bold magenta]")
        for j, variation in enumerate(variations, 1):
            console.print(f"  {j}. {variation}")
        
        # Show negative prompts
        negatives = optimizer.get_negative_prompts(prompt)
        console.print(f"\n[bold red]🚫 Negative Prompts:[/bold red] {', '.join(negatives)}")
        
        console.print("\n" + "─" * 80)
    
    # Complexity analysis demo
    console.print("\n[bold cyan]📊 Complexity Analysis Demo[/bold cyan]")
    
    complex_prompt = "A highly detailed, photorealistic portrait of a young woman with flowing auburn hair, wearing a vintage Victorian dress, sitting in a ornate chair by a large bay window with soft natural lighting filtering through lace curtains, captured with a professional camera using shallow depth of field and golden hour lighting, high quality, 8k resolution, masterpiece"
    
    complexity = optimizer.analyze_prompt_complexity(complex_prompt)
    
    complexity_panel = Panel(
        f"[bold]Complexity Level:[/bold] {complexity['complexity_level'].title()}\n"
        f"[bold]Word Count:[/bold] {complexity['word_count']}\n"
        f"[bold]Readability Score:[/bold] {complexity['readability_score']:.2f}/1.0\n"
        f"[bold]Technical Terms:[/bold] {complexity['technical_terms']}\n"
        f"[bold]Artistic Terms:[/bold] {complexity['artistic_terms']}\n"
        f"[bold]Suggestions:[/bold] {', '.join(complexity['suggestions'])}",
        title="Complexity Analysis",
        border_style="green"
    )
    console.print(complexity_panel)
    
    # Final summary
    summary_panel = Panel(
        "[bold green]🎉 AI Prompt Optimizer Features:[/bold green]\n\n"
        "✅ Intelligent prompt analysis\n"
        "✅ Style and quality suggestions\n"
        "✅ Automatic prompt optimization\n"
        "✅ Style variations generation\n"
        "✅ Negative prompt suggestions\n"
        "✅ Complexity analysis\n"
        "✅ Confidence scoring\n"
        "✅ Subject category detection\n\n"
        "[bold yellow]💡 Use this to improve your image generation prompts![/bold yellow]",
        title="Optimizer Complete",
        border_style="green"
    )
    console.print(summary_panel)

if __name__ == "__main__":
    main()
