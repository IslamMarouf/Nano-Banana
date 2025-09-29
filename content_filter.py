#!/usr/bin/env python3
"""
Content filtering and NSFW detection system for Nano Banana Image Generator
"""

import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import requests

console = Console()

@dataclass
class ContentWarning:
    """Data class for content warnings"""
    category: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    confidence: float
    suggested_action: str

class ContentFilter:
    """Advanced content filtering and NSFW detection system"""
    
    def __init__(self):
        self.nsfw_keywords = self._load_nsfw_keywords()
        self.violence_keywords = self._load_violence_keywords()
        self.hate_speech_patterns = self._load_hate_speech_patterns()
        self.age_inappropriate = self._load_age_inappropriate()
        self.legal_issues = self._load_legal_issues()
        self.filter_history = []
        
    def _load_nsfw_keywords(self) -> List[str]:
        """Load NSFW keywords for detection"""
        return [
            "nude", "naked", "sex", "sexual", "porn", "adult", "explicit",
            "erotic", "fetish", "bdsm", "masturbat", "orgasm", "genital",
            "breast", "nipple", "penis", "vagina", "butt", "ass", "asshole",
            "pussy", "cock", "dick", "boob", "tit", "fuck", "fucking",
            "horny", "sexy", "hot", "seductive", "provocative", "suggestive"
        ]
    
    def _load_violence_keywords(self) -> List[str]:
        """Load violence-related keywords"""
        return [
            "kill", "murder", "death", "die", "dead", "corpse", "blood",
            "violence", "fight", "attack", "weapon", "gun", "knife", "bomb",
            "explosion", "war", "battle", "torture", "hurt", "pain", "injury",
            "wound", "cut", "stab", "shoot", "beat", "punch", "kick"
        ]
    
    def _load_hate_speech_patterns(self) -> List[str]:
        """Load hate speech patterns"""
        return [
            r"\b(hate|hating)\s+(gay|lesbian|trans|black|white|jew|muslim|christian)",
            r"\b(kill|murder)\s+(all|every)\s+(gay|lesbian|trans|black|jew|muslim)",
            r"\b(disgusting|disgusting)\s+(gay|lesbian|trans|black|jew|muslim)",
            r"\b(faggot|nigger|kike|chink|spic|wetback)",
            r"\b(white\s+power|supremacist|nazi|fascist)",
            r"\b(terrorist|jihad|islamic\s+state|isis)"
        ]
    
    def _load_age_inappropriate(self) -> List[str]:
        """Load age-inappropriate content keywords"""
        return [
            "child", "kid", "baby", "infant", "toddler", "minor", "underage",
            "school", "student", "teen", "teenage", "young", "little girl",
            "little boy", "pedophile", "lolita", "schoolgirl", "schoolboy"
        ]
    
    def _load_legal_issues(self) -> List[str]:
        """Load legally problematic content"""
        return [
            "copyright", "trademark", "brand", "logo", "celebrity", "famous",
            "celebrity", "actor", "actress", "singer", "musician", "athlete",
            "politician", "president", "prime minister", "government", "official"
        ]
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Comprehensive content analysis of a prompt"""
        analysis = {
            "original_prompt": prompt,
            "is_safe": True,
            "warnings": [],
            "risk_level": "low",
            "confidence": 0.0,
            "suggested_actions": []
        }
        
        prompt_lower = prompt.lower()
        warnings = []
        
        # Check NSFW content
        nsfw_warnings = self._check_nsfw_content(prompt_lower)
        warnings.extend(nsfw_warnings)
        
        # Check violence
        violence_warnings = self._check_violence_content(prompt_lower)
        warnings.extend(violence_warnings)
        
        # Check hate speech
        hate_warnings = self._check_hate_speech(prompt_lower)
        warnings.extend(hate_warnings)
        
        # Check age-inappropriate content
        age_warnings = self._check_age_inappropriate(prompt_lower)
        warnings.extend(age_warnings)
        
        # Check legal issues
        legal_warnings = self._check_legal_issues(prompt_lower)
        warnings.extend(legal_warnings)
        
        # Calculate risk level
        if warnings:
            analysis["warnings"] = warnings
            analysis["is_safe"] = False
            
            # Determine risk level based on highest severity
            severities = [w.severity for w in warnings]
            if "critical" in severities:
                analysis["risk_level"] = "critical"
            elif "high" in severities:
                analysis["risk_level"] = "high"
            elif "medium" in severities:
                analysis["risk_level"] = "medium"
            else:
                analysis["risk_level"] = "low"
            
            # Calculate confidence
            analysis["confidence"] = max([w.confidence for w in warnings])
            
            # Generate suggested actions
            analysis["suggested_actions"] = self._generate_suggested_actions(warnings)
        
        # Log analysis
        self._log_analysis(analysis)
        
        return analysis
    
    def _check_nsfw_content(self, prompt: str) -> List[ContentWarning]:
        """Check for NSFW content"""
        warnings = []
        
        for keyword in self.nsfw_keywords:
            if keyword in prompt:
                severity = "high" if keyword in ["sex", "porn", "explicit", "nude", "naked"] else "medium"
                confidence = 0.9 if keyword in ["sex", "porn", "explicit"] else 0.7
                
                warnings.append(ContentWarning(
                    category="nsfw",
                    severity=severity,
                    description=f"Contains NSFW keyword: '{keyword}'",
                    confidence=confidence,
                    suggested_action="Remove or replace NSFW content"
                ))
        
        return warnings
    
    def _check_violence_content(self, prompt: str) -> List[ContentWarning]:
        """Check for violent content"""
        warnings = []
        
        for keyword in self.violence_keywords:
            if keyword in prompt:
                severity = "high" if keyword in ["kill", "murder", "death", "blood"] else "medium"
                confidence = 0.8 if keyword in ["kill", "murder", "death"] else 0.6
                
                warnings.append(ContentWarning(
                    category="violence",
                    severity=severity,
                    description=f"Contains violence-related keyword: '{keyword}'",
                    confidence=confidence,
                    suggested_action="Remove or replace violent content"
                ))
        
        return warnings
    
    def _check_hate_speech(self, prompt: str) -> List[ContentWarning]:
        """Check for hate speech patterns"""
        warnings = []
        
        for pattern in self.hate_speech_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                warnings.append(ContentWarning(
                    category="hate_speech",
                    severity="critical",
                    description=f"Contains hate speech pattern: '{pattern}'",
                    confidence=0.95,
                    suggested_action="Block content - contains hate speech"
                ))
        
        return warnings
    
    def _check_age_inappropriate(self, prompt: str) -> List[ContentWarning]:
        """Check for age-inappropriate content"""
        warnings = []
        
        for keyword in self.age_inappropriate:
            if keyword in prompt:
                severity = "critical" if keyword in ["pedophile", "lolita", "underage"] else "high"
                confidence = 0.95 if keyword in ["pedophile", "lolita"] else 0.8
                
                warnings.append(ContentWarning(
                    category="age_inappropriate",
                    severity=severity,
                    description=f"Contains age-inappropriate content: '{keyword}'",
                    confidence=confidence,
                    suggested_action="Block content - inappropriate for minors"
                ))
        
        return warnings
    
    def _check_legal_issues(self, prompt: str) -> List[ContentWarning]:
        """Check for potential legal issues"""
        warnings = []
        
        for keyword in self.legal_issues:
            if keyword in prompt:
                warnings.append(ContentWarning(
                    category="legal",
                    severity="medium",
                    description=f"May contain copyrighted content: '{keyword}'",
                    confidence=0.6,
                    suggested_action="Review for copyright compliance"
                ))
        
        return warnings
    
    def _generate_suggested_actions(self, warnings: List[ContentWarning]) -> List[str]:
        """Generate suggested actions based on warnings"""
        actions = []
        
        critical_warnings = [w for w in warnings if w.severity == "critical"]
        high_warnings = [w for w in warnings if w.severity == "high"]
        
        if critical_warnings:
            actions.append("🚫 BLOCK: Content contains critical violations")
        elif high_warnings:
            actions.append("⚠️ WARN: High-risk content detected")
        
        if any(w.category == "nsfw" for w in warnings):
            actions.append("🔞 Add age verification")
        
        if any(w.category == "violence" for w in warnings):
            actions.append("⚠️ Add violence warning")
        
        if any(w.category == "hate_speech" for w in warnings):
            actions.append("🚫 Block hate speech content")
        
        if any(w.category == "legal" for w in warnings):
            actions.append("📋 Review for legal compliance")
        
        if not actions:
            actions.append("✅ Content appears safe")
        
        return actions
    
    def _log_analysis(self, analysis: Dict[str, Any]):
        """Log analysis for monitoring and improvement"""
        log_entry = {
            "timestamp": time.time(),
            "prompt_hash": hash(analysis["original_prompt"]),
            "is_safe": analysis["is_safe"],
            "risk_level": analysis["risk_level"],
            "warning_count": len(analysis["warnings"]),
            "categories": list(set([w.category for w in analysis["warnings"]]))
        }
        
        self.filter_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.filter_history) > 1000:
            self.filter_history = self.filter_history[-1000:]
    
    def get_safe_alternative(self, prompt: str) -> str:
        """Generate a safe alternative to a problematic prompt"""
        safe_alternatives = {
            "nude": "clothed figure",
            "naked": "dressed person",
            "sexy": "attractive",
            "hot": "appealing",
            "violence": "action",
            "kill": "overcome",
            "death": "transformation",
            "blood": "energy",
            "weapon": "tool",
            "fight": "competition",
            "war": "conflict resolution",
            "hate": "dislike",
            "fuck": "strong emotion"
        }
        
        safe_prompt = prompt.lower()
        
        for problematic, safe in safe_alternatives.items():
            safe_prompt = safe_prompt.replace(problematic, safe)
        
        return safe_prompt.title()
    
    def get_filter_statistics(self) -> Dict[str, Any]:
        """Get filtering statistics"""
        total_analyzed = len(self.filter_history)
        blocked_count = len([h for h in self.filter_history if not h["is_safe"]])
        
        category_counts = {}
        for entry in self.filter_history:
            for category in entry.get("categories", []):
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_analyzed": total_analyzed,
            "blocked_count": blocked_count,
            "block_rate": (blocked_count / total_analyzed * 100) if total_analyzed > 0 else 0,
            "category_counts": category_counts,
            "most_common_issues": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def display_analysis(self, analysis: Dict[str, Any]):
        """Display content analysis results"""
        console.print("\n[bold cyan]🔍 Content Analysis Results[/bold cyan]")
        
        # Summary panel
        risk_color = {
            "low": "green",
            "medium": "yellow", 
            "high": "red",
            "critical": "red"
        }
        
        status_icon = "✅" if analysis["is_safe"] else "❌"
        status_text = "SAFE" if analysis["is_safe"] else f"RISK: {analysis['risk_level'].upper()}"
        
        summary_panel = Panel(
            f"[bold]Status:[/bold] {status_icon} {status_text}\n"
            f"[bold]Confidence:[/bold] {analysis['confidence']:.2f}\n"
            f"[bold]Warnings:[/bold] {len(analysis['warnings'])}\n"
            f"[bold]Original Prompt:[/bold] {analysis['original_prompt'][:100]}...",
            title="Analysis Summary",
            border_style=risk_color.get(analysis["risk_level"], "red")
        )
        console.print(summary_panel)
        
        # Warnings table
        if analysis["warnings"]:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Category", style="cyan", width=15)
            table.add_column("Severity", style="yellow", width=10)
            table.add_column("Description", style="green", width=40)
            table.add_column("Confidence", style="blue", width=12)
            table.add_column("Action", style="red", width=25)
            
            for warning in analysis["warnings"]:
                severity_color = {
                    "low": "green",
                    "medium": "yellow",
                    "high": "red",
                    "critical": "red"
                }
                
                table.add_row(
                    warning.category.replace("_", " ").title(),
                    f"[{severity_color[warning.severity]}]{warning.severity.upper()}[/{severity_color[warning.severity]}]",
                    warning.description,
                    f"{warning.confidence:.2f}",
                    warning.suggested_action
                )
            
            console.print(table)
        
        # Suggested actions
        if analysis["suggested_actions"]:
            console.print("\n[bold red]🚨 Suggested Actions:[/bold red]")
            for action in analysis["suggested_actions"]:
                console.print(f"  • {action}")

def demo_content_filtering():
    """Demo content filtering system"""
    banner = Panel(
        "[bold blue]🛡️ Content Filter Demo[/bold blue]\n\n"
        "Demonstrating AI-powered content filtering and safety features",
        title="Content Safety",
        border_style="blue"
    )
    console.print(banner)
    
    filter_system = ContentFilter()
    
    # Demo prompts with various content types
    demo_prompts = [
        "A beautiful sunset over mountains",
        "A nude woman in an artistic pose",
        "A violent fight scene with blood",
        "A cute cat sitting in a garden",
        "Hate speech against minorities",
        "A professional portrait of a businesswoman",
        "A child in inappropriate situation",
        "A peaceful landscape with flowers",
        "Sexual content with explicit details",
        "A vintage car on a country road"
    ]
    
    console.print("\n[bold cyan]🔍 Analyzing Demo Prompts[/bold cyan]")
    
    safe_count = 0
    blocked_count = 0
    
    for i, prompt in enumerate(demo_prompts, 1):
        console.print(f"\n[bold yellow]Prompt {i}:[/bold yellow] {prompt}")
        
        analysis = filter_system.analyze_prompt(prompt)
        filter_system.display_analysis(analysis)
        
        if analysis["is_safe"]:
            safe_count += 1
        else:
            blocked_count += 1
        
        # Show safe alternative if needed
        if not analysis["is_safe"]:
            safe_alternative = filter_system.get_safe_alternative(prompt)
            console.print(f"\n[bold green]✨ Safe Alternative:[/bold green] {safe_alternative}")
        
        console.print("\n" + "─" * 80)
    
    # Show statistics
    stats = filter_system.get_filter_statistics()
    
    stats_panel = Panel(
        f"[bold blue]📊 Filtering Statistics[/bold blue]\n\n"
        f"Total Analyzed: {stats['total_analyzed']}\n"
        f"Blocked Content: {stats['blocked_count']}\n"
        f"Block Rate: {stats['block_rate']:.1f}%\n"
        f"Safe Content: {safe_count}\n"
        f"Blocked Content: {blocked_count}\n\n"
        f"[bold]Most Common Issues:[/bold]\n" + 
        "\n".join([f"• {category}: {count}" for category, count in stats['most_common_issues']]),
        title="Filter Statistics",
        border_style="blue"
    )
    console.print(stats_panel)
    
    # Feature summary
    features_panel = Panel(
        "[bold green]🎉 Content Filter Features:[/bold green]\n\n"
        "✅ NSFW content detection\n"
        "✅ Violence and harmful content filtering\n"
        "✅ Hate speech pattern recognition\n"
        "✅ Age-inappropriate content detection\n"
        "✅ Legal compliance checking\n"
        "✅ Risk level assessment\n"
        "✅ Confidence scoring\n"
        "✅ Safe alternative suggestions\n"
        "✅ Filtering statistics and analytics\n"
        "✅ Real-time content monitoring\n\n"
        "[bold yellow]💡 Keep your content safe and appropriate![/bold yellow]",
        title="Content Filter Complete",
        border_style="green"
    )
    console.print(features_panel)

def main():
    """Main function for content filtering demo"""
    demo_content_filtering()

if __name__ == "__main__":
    main()
