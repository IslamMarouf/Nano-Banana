import os
import asyncio
import requests
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.prompt import Confirm
from utils import save_image_from_url
from config_manager import config

# Initialize Rich console
console = Console()

def print_banner():
    banner_text = Text("🍌 Nano Banana Image Generator", style="bold blue")
    console.print(Panel(banner_text, style="blue", padding=(1, 2)))

def get_user_choice():
    while True:
        console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
        console.print("1. [green]Create a new image[/green]")
        console.print("2. [yellow]Edit an existing image[/yellow]")
        console.print("3. [blue]Settings[/blue]")
        console.print("4. [red]Exit[/red]")
        
        try:
            choice = Prompt.ask("\nEnter your choice", choices=["1", "2", "3", "4"], default="1")
            return choice
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            return "4"
        except Exception:
            console.print("[red]Invalid choice. Please enter 1, 2, 3, or 4.[/red]")
            continue

def get_image_path():
    while True:
        try:
            path = Prompt.ask("Enter the original image path (local file or URL)")
            
            # Check if it's a local file
            if not path.startswith(('http://', 'https://')):
                if not os.path.exists(path):
                    console.print(f"[red]File not found: {path}[/red]")
                    continue
            
            return path
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled...[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue

def get_prompt(prompt_type="creation"):
    while True:
        try:
            prompt = Prompt.ask(f"Enter your {prompt_type} prompt")
            if prompt:
                return prompt
            console.print("[red]Prompt cannot be empty. Please try again.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled...[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue

def show_settings_menu():
    """Display and manage application settings"""
    while True:
        console.print("\n[bold cyan]Settings Menu[/bold cyan]")
        
        # Create settings table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan", width=25)
        table.add_column("Current Value", style="green")
        table.add_column("Description", style="yellow")
        
        # Add current settings
        table.add_row(
            "Output Format", 
            config.get('default_settings', 'output_format', 'jpg'),
            "Image format (jpg, png, webp)"
        )
        table.add_row(
            "Resolution", 
            config.get('default_settings', 'resolution', '1024x1024'),
            "Image dimensions"
        )
        table.add_row(
            "Quality", 
            config.get('default_settings', 'quality', 'high'),
            "Image quality (low, medium, high)"
        )
        table.add_row(
            "Show Progress", 
            str(config.get('ui_settings', 'show_progress', True)),
            "Display progress bars"
        )
        table.add_row(
            "Fallback Enabled", 
            str(config.get('advanced_settings', 'fallback_enabled', True)),
            "Use fallback when API fails"
        )
        
        console.print(table)
        
        console.print("\n[bold cyan]Settings Options:[/bold cyan]")
        console.print("1. [green]Change Output Format[/green]")
        console.print("2. [green]Change Resolution[/green]")
        console.print("3. [green]Toggle Progress Display[/green]")
        console.print("4. [green]Toggle Fallback[/green]")
        console.print("5. [yellow]View Full Configuration[/yellow]")
        console.print("6. [yellow]Reset to Defaults[/yellow]")
        console.print("7. [red]Back to Main Menu[/red]")
        
        choice = Prompt.ask("\nChoose an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")
        
        if choice == "1":
            new_format = Prompt.ask(
                "Enter output format", 
                choices=["jpg", "png", "webp"], 
                default=config.get('default_settings', 'output_format', 'jpg')
            )
            config.set('default_settings', 'output_format', new_format)
            console.print(f"[green]✅ Output format set to {new_format}[/green]")
            
        elif choice == "2":
            new_resolution = Prompt.ask(
                "Enter resolution", 
                choices=["512x512", "1024x1024", "2048x2048"], 
                default=config.get('default_settings', 'resolution', '1024x1024')
            )
            config.set('default_settings', 'resolution', new_resolution)
            console.print(f"[green]✅ Resolution set to {new_resolution}[/green]")
            
        elif choice == "3":
            current = config.get('ui_settings', 'show_progress', True)
            new_value = not current
            config.set('ui_settings', 'show_progress', new_value)
            console.print(f"[green]✅ Progress display {'enabled' if new_value else 'disabled'}[/green]")
            
        elif choice == "4":
            current = config.get('advanced_settings', 'fallback_enabled', True)
            new_value = not current
            config.set('advanced_settings', 'fallback_enabled', new_value)
            console.print(f"[green]✅ Fallback {'enabled' if new_value else 'disabled'}[/green]")
            
        elif choice == "5":
            config.show_config()
            
        elif choice == "6":
            if Confirm.ask("Are you sure you want to reset all settings to defaults?"):
                config.reset_to_defaults()
                console.print("[green]✅ Settings reset to defaults[/green]")
            else:
                console.print("[yellow]Settings reset cancelled[/yellow]")
                
        elif choice == "7":
            break

async def main():
    print_banner()
    
    # Create output directory
    output_dir = "output_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if local server is running
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking server status...", total=None)
        
        try:
            response = requests.get('http://127.0.0.1:10000/health', timeout=5)
            console.print("✅ [green]Local server is running[/green]")
            use_local_server = True
        except:
            console.print("❌ [yellow]Local server not found, using direct API calls[/yellow]")
            from utils import ImageGenerator
            generator = ImageGenerator()
            use_local_server = False
    
    while True:
        choice = get_user_choice()
        
        if choice == '3':  # Settings
            show_settings_menu()
            continue
        elif choice == '4':  # Exit
            console.print("\n[bold green]Thank you for using Nano Banana Image Generator! 🍌[/bold green]")
            break
        
        try:
            if choice == '1':  # Create new image
                prompt = get_prompt("creation")
                if prompt is None:
                    console.print("[yellow]Prompt input cancelled.[/yellow]")
                    continue
                    
                console.print(f"\n[bold cyan]Creating image with prompt:[/bold cyan] [italic]'{prompt}'[/italic]")
                
                # Create progress bar for image generation (if enabled)
                show_progress = config.get('ui_settings', 'show_progress', True)
                
                if show_progress:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TimeElapsedColumn(),
                        console=console,
                    ) as progress:
                        task = progress.add_task("Generating image...", total=100)
                        
                        # Simulate progress updates
                        for i in range(0, 101, 10):
                            progress.update(task, advance=10, description=f"Generating image... ({i}%)")
                            await asyncio.sleep(0.1)
                        
                        if use_local_server:
                            response = requests.post('http://127.0.0.1:10000/v1/image/generations', 
                                                   json={'prompt': prompt}, timeout=120)
                            image_url = response.json()['data'][0]['url']
                        else:
                            image_url = await generator.create_image(prompt)
                else:
                    console.print("[yellow]Generating image... Please wait...[/yellow]")
                    if use_local_server:
                        response = requests.post('http://127.0.0.1:10000/v1/image/generations', 
                                               json={'prompt': prompt}, timeout=120)
                        image_url = response.json()['data'][0]['url']
                    else:
                        image_url = await generator.create_image(prompt)
                
            elif choice == '2':  # Edit existing image
                image_path = get_image_path()
                if image_path is None:
                    console.print("[yellow]Image path input cancelled.[/yellow]")
                    continue
                    
                prompt = get_prompt("edit")
                if prompt is None:
                    console.print("[yellow]Prompt input cancelled.[/yellow]")
                    continue
                    
                console.print(f"\n[bold cyan]Editing image with prompt:[/bold cyan] [italic]'{prompt}'[/italic]")
                
                # Create progress bar for image editing (if enabled)
                if show_progress:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TimeElapsedColumn(),
                        console=console,
                    ) as progress:
                        task = progress.add_task("Processing image...", total=100)
                        
                        # Simulate progress updates
                        for i in range(0, 101, 10):
                            progress.update(task, advance=10, description=f"Processing image... ({i}%)")
                            await asyncio.sleep(0.1)
                        
                        if use_local_server:
                            response = requests.post('http://127.0.0.1:10000/v1/image/generations', 
                                                   json={'prompt': prompt, 'image_url': image_path}, timeout=120)
                            image_url = response.json()['data'][0]['url']
                        else:
                            image_url = await generator.edit_image(prompt, image_path)
                else:
                    console.print("[yellow]Processing image... Please wait...[/yellow]")
                    if use_local_server:
                        response = requests.post('http://127.0.0.1:10000/v1/image/generations', 
                                               json={'prompt': prompt, 'image_url': image_path}, timeout=120)
                        image_url = response.json()['data'][0]['url']
                    else:
                        image_url = await generator.edit_image(prompt, image_path)
            
            # Save the generated image with progress
            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    save_task = progress.add_task("Saving image to output folder...", total=None)
                    saved_path = save_image_from_url(
                        image_url, 
                        output_dir, 
                        config.get('default_settings', 'output_format', 'jpg')
                    )
            else:
                console.print("[yellow]Saving image to output folder...[/yellow]")
                saved_path = save_image_from_url(
                    image_url, 
                    output_dir, 
                    config.get('default_settings', 'output_format', 'jpg')
                )
            
            # Success message with nice formatting
            success_panel = Panel(
                f"[bold green]✅ Process completed successfully![/bold green]\n\n"
                f"[cyan]Image saved to:[/cyan] [yellow]{saved_path}[/yellow]\n"
                f"[cyan]Original URL:[/cyan] [blue]{image_url}[/blue]",
                title="Success",
                border_style="green"
            )
            console.print(success_panel)
            
        except Exception as e:
            error_panel = Panel(
                f"[bold red]❌ Error: {str(e)}[/bold red]\n\n"
                f"[yellow]Please try again.[/yellow]",
                title="Error",
                border_style="red"
            )
            console.print(error_panel)
        
        console.print("\n" + "─" * 60)

if __name__ == "__main__":
    asyncio.run(main())