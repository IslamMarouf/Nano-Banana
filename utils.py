import os
import time
import requests
from pathlib import Path
from typing import Optional, Tuple
from config_manager import config
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

def get_image_format_from_url(url: str) -> str:
    """Detect image format from URL or content"""
    # Check URL extension first
    url_lower = url.lower()
    if url_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp')):
        ext = url_lower.split('.')[-1]
        if ext in ['jpg', 'jpeg']:
            return 'jpg'
        return ext
    
    # Default to configured format
    return config.get('default_settings', 'output_format', 'jpg')

def save_image_from_url(image_url: str, output_dir: str, custom_format: Optional[str] = None) -> str:
    """Download and save image from URL with format detection and better error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Make request with better error handling
        response = requests.get(image_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Detect format
        content_type = response.headers.get('content-type', '').lower()
        if custom_format:
            file_format = custom_format
        elif 'image/png' in content_type:
            file_format = 'png'
        elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
            file_format = 'jpg'
        elif 'image/webp' in content_type:
            file_format = 'webp'
        else:
            file_format = get_image_format_from_url(image_url)
        
        # Generate filename with timestamp and format
        timestamp = int(time.time())
        filename = f"generated_image_{timestamp}.{file_format}"
        filepath = os.path.join(output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save image with progress for large files
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        # Verify file was saved correctly
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath
        else:
            raise Exception("Saved file is empty or doesn't exist")
        
    except requests.exceptions.Timeout:
        raise Exception("Request timed out - the image server is taking too long to respond")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection error - unable to reach the image server")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error {e.response.status_code}: {e.response.reason}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except OSError as e:
        raise Exception(f"File system error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to save image: {str(e)}")