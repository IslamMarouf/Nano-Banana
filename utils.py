import os
import time
import requests
from main import VisualGPTProvider, upload_image_to_uguu, IMAGE_UPLOAD_URL

class ImageGenerator:
    def __init__(self):
        self.provider = VisualGPTProvider()
    
    async def create_image(self, prompt):
        """Create a new image from prompt"""
        return await self.provider.generate_image(prompt)
    
    async def edit_image(self, prompt, image_path):
        """Edit an existing image with prompt"""
        # If it's a local file, upload it first
        if not image_path.startswith(('http://', 'https://')):
            print("Uploading local image...")
            image_url = upload_local_image(image_path)
        else:
            image_url = image_path
        
        return await self.provider.generate_image(prompt, image_url)

def upload_local_image(file_path):
    """Upload a local image file and return URL"""
    try:
        with open(file_path, 'rb') as f:
            files = {'files[]': (os.path.basename(file_path), f, 'image/jpeg')}
            response = requests.post('https://uguu.se/upload', files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('files'):
                    return data['files'][0]['url']
        
        # Fallback: return default image URL
        print("Warning: Upload failed, using default image")
        return "https://picsum.photos/1024/1024"
        
    except Exception as e:
        print(f"Warning: Upload error: {e}, using default image")
        return "https://picsum.photos/1024/1024"

def save_image_from_url(image_url, output_dir):
    """Download and save image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Generate filename
        timestamp = int(time.time())
        filename = f"generated_image_{timestamp}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
        
    except Exception as e:
        raise Exception(f"Failed to save image: {e}")