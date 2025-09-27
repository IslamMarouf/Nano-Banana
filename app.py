import os
import asyncio
import requests
from utils import save_image_from_url

def print_banner():
    print("=" * 50)
    print(" Nano Banana Image Generator")
    print("=" * 50)

def get_user_choice():
    while True:
        print("\nWhat would you like to do?")
        print("1. Create a new image")
        print("2. Edit an existing image")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")

def get_image_path():
    while True:
        path = input("Enter the original image path (local file or URL): ").strip()
        if not path:
            print("Path cannot be empty. Please try again.")
            continue
        
        # Check if it's a local file
        if not path.startswith(('http://', 'https://')):
            if not os.path.exists(path):
                print(f"File not found: {path}")
                continue
        
        return path

def get_prompt(prompt_type="creation"):
    while True:
        prompt = input(f"Enter your {prompt_type} prompt: ").strip()
        if prompt:
            return prompt
        print("Prompt cannot be empty. Please try again.")

async def main():
    print_banner()
    
    # Create output directory
    output_dir = "output_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if local server is running
    try:
        response = requests.get('http://127.0.0.1:10000/health', timeout=5)
        print("✓ Local server is running")
        use_local_server = True
    except:
        print("✗ Local server not found, using direct API calls")
        from utils import ImageGenerator
        generator = ImageGenerator()
        use_local_server = False
    
    while True:
        choice = get_user_choice()
        
        if choice == '3':
            print("\nThank you for using Nano Banana Image Generator!")
            break
        
        try:
            if choice == '1':  # Create new image
                prompt = get_prompt("creation")
                print(f"\nCreating image with prompt: '{prompt}'")
                print("Generating image... Please wait...")
                
                if use_local_server:
                    response = requests.post('http://127.0.0.1:10000/v1/image/generations', 
                                           json={'prompt': prompt}, timeout=120)
                    image_url = response.json()['data'][0]['url']
                else:
                    image_url = await generator.create_image(prompt)
                
            elif choice == '2':  # Edit existing image
                image_path = get_image_path()
                prompt = get_prompt("edit")
                print(f"\nEditing image with prompt: '{prompt}'")
                print("Processing image... Please wait...")
                
                if use_local_server:
                    response = requests.post('http://127.0.0.1:10000/v1/image/generations', 
                                           json={'prompt': prompt, 'image_url': image_path}, timeout=120)
                    image_url = response.json()['data'][0]['url']
                else:
                    image_url = await generator.edit_image(prompt, image_path)
            
            # Save the generated image
            print("Saving image to output folder...")
            saved_path = save_image_from_url(image_url, output_dir)
            
            print(f"\nProcess completed successfully!")
            print(f"Image saved to: {saved_path}")
            print(f"Original URL: {image_url}")
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")
        
        print("\n" + "-" * 50)

if __name__ == "__main__":
    asyncio.run(main())