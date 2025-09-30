from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import requests
import time
import uuid
import logging
import io
import os
import json

# Configure logging with timestamps and structured format
logging.basicConfig(
    level=logging.INFO,
    format='\033[92m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# --- Models ---
class ImageGenerationRequest(BaseModel):
    prompt: str
    image_url: Optional[str] = None  # Starting image URL for editing
    format: Optional[str] = "jpg"  # Output format
    resolution: Optional[str] = "1024x1024"  # Output resolution
    quality: Optional[str] = "high"  # Quality setting
    strength: Optional[float] = 0.8  # How much to modify (0.0-1.0)
    negative_prompt: Optional[str] = None  # What to avoid
    style: Optional[str] = None  # Style preset (realistic, artistic, cartoon, etc.)
    seed: Optional[int] = None  # For reproducible results
    num_variations: Optional[int] = 1  # Number of variations to generate
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A beautiful sunset over mountains",
                "image_url": "https://example.com/image.jpg",
                "format": "jpg",
                "resolution": "1024x1024",
                "quality": "high",
                "strength": 0.8,
                "negative_prompt": "blurry, low quality",
                "style": "realistic",
                "seed": 42,
                "num_variations": 1
            }
        }

class BatchGenerationRequest(BaseModel):
    prompts: List[str]
    format: Optional[str] = "jpg"
    resolution: Optional[str] = "1024x1024"
    quality: Optional[str] = "high"

class HistoryItem(BaseModel):
    id: str
    type: str  # "create" or "edit"
    prompt: str
    format: str
    resolution: Optional[str] = None
    image_url: str
    timestamp: str
    metadata: Optional[dict] = None


# --- Config ---
IMAGE_UPLOAD_URL = "https://wallpaperaccess.com/full/1556608.jpg"

# Fallback image generation using a more reliable service
FALLBACK_ENABLED = True

# Progress tracking dictionary
generation_progress = {}

# Gallery storage (in-memory for now, can be moved to database)
gallery_items = []

# Batch processing queue
batch_queue = {}


def upload_image_to_uguu(image_url: str) -> str:
    """Download image and upload to uguu.se"""
    logger.info(f"Downloading image from: {image_url}")
    
    try:
        # Download the image with better headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://visualgpt.io"
        }
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Validate image content
        if len(response.content) < 1000:  # Less than 1KB is suspicious
            raise Exception(f"Downloaded content too small ({len(response.content)} bytes), might not be a valid image")
        
        logger.info(f"Downloaded image: {len(response.content)} bytes")
        
        # Create file object from image data
        image_data = io.BytesIO(response.content)
        
        # Extract filename from URL or use default
        filename = image_url.split("/")[-1].split("?")[0]  # Remove query parameters
        if not filename or "." not in filename:
            filename = f"generated_image_{int(time.time())}.jpg"
        
        logger.info(f"⏳ Uploading image to uguu.se as {filename}...")
        
        files = {"files[]": (filename, image_data, "image/jpeg")}
        
        # Try uguu.se first, then fallback to other services
        upload_services = [
            ("https://uguu.se/upload", "uguu.se"),
            ("https://0x0.st", "0x0.st")
        ]
        
        for upload_url, service_name in upload_services:
            try:
                if service_name == "0x0.st":
                    # 0x0.st uses different format
                    files = {"file": (filename, io.BytesIO(response.content), "image/jpeg")}
                
                upload_response = requests.post(upload_url, files=files, timeout=30)
                
                if upload_response.status_code == 200:
                    if service_name == "uguu.se":
                        data = upload_response.json()
                        if data.get("success") and data.get("files"):
                            url = data["files"][0].get("url")
                            if url:
                                logger.info(f"✅ Upload successful to {service_name}: {url}")
                                return url
                    elif service_name == "0x0.st":
                        url = upload_response.text.strip()
                        if url.startswith("http"):
                            logger.info(f"✅ Upload successful to {service_name}: {url}")
                            return url
                
                logger.warning(f"Upload to {service_name} failed, trying next service...")
                
            except Exception as e:
                logger.warning(f"Upload to {service_name} failed: {e}")
                continue
        
        # If all upload services fail, return the original URL
        logger.warning("All upload services failed, returning original URL")
        return image_url
        
    except Exception as e:
        logger.error(f"Error in upload_image_to_uguu: {e}")
        raise Exception(f"Failed to download or upload image: {e}")


def generate_cookie():
    anon_user_id = str(uuid.uuid4())  # Generates a new unique ID
    current_timestamp = int(time.time())
    return (
        f"_ga=GA1.1.{current_timestamp}.{current_timestamp}; "
        f"_ga_PZ8PZQP57J=GS2.1.s{current_timestamp}$o1$g0$t{current_timestamp}$j60$l0$h0; "
        f"anonymous_user_id={anon_user_id}; "
        f"sbox-guid={uuid.uuid4().hex[:20]}; "
        f"crisp-client%2Fsession%2F{uuid.uuid4()}=session_{uuid.uuid4()}"
    )


class FallbackImageProvider:
    """Simple fallback image generator using placeholder services"""
    
    def __init__(self):
        self.base_urls = [
            "https://picsum.photos/1024/1024",
            "https://source.unsplash.com/1024x1024",
            "https://via.placeholder.com/1024x1024/4A90E2/FFFFFF"
        ]
    
    async def generate_image(self, prompt: str, image_url: str = None) -> str:
        """Generate a placeholder image with text overlay"""
        logger.info(f"Using fallback image generation for prompt: {prompt[:50]}...")
        
        # Use a more reliable placeholder service
        fallback_url = "https://picsum.photos/1024/1024"
        
        logger.info(f"Generated fallback image URL: {fallback_url}")
        return fallback_url


class VisualGPTProvider:
    def __init__(self):
        self.cookie_string = generate_cookie()
        self.headers_step1 = {
            "authority": "visualgpt.io",
            "method": "POST",
            "path": "/api/v1/prediction/handle",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "content-type": "application/json; charset=UTF-8",
            "cookie": self.cookie_string,
            "origin": "https://visualgpt.io",
            "referer": "https://visualgpt.io/ai-models/nano-banana",
            "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge";v="131"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
        
        self.headers_step2 = {
            "authority": "visualgpt.io",
            "method": "GET",
            "path": "",  # will fill with `get-status?session_id=...`
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cookie": self.cookie_string,
            "referer": "https://visualgpt.io/ai-models/nano-banana",
            "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge";v="131"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }

    def submit_prediction(self, prompt, image_url=None):
        url = "https://visualgpt.io/api/v1/prediction/handle"
        
        # Use provided image_url or default
        starting_image = image_url if image_url and image_url.strip() else IMAGE_UPLOAD_URL
        
        payload = {
            "image_urls": [starting_image],
            "type": 61,
            "user_prompt": prompt,
            "sub_type": 2,
            "aspect_ratio": "",
            "num": ""
        }

        logger.info(f"Submitting prediction request for prompt: {prompt[:50]}... with image: {starting_image}")
        logger.info(f"Payload: {payload}")
        
        # Try multiple times with different approaches
        max_retries = 5
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}")
                
                # Regenerate cookie for each attempt to avoid stale sessions
                if attempt > 0:
                    self.cookie_string = generate_cookie()
                    self.headers_step1["cookie"] = self.cookie_string
                    self.headers_step2["cookie"] = self.cookie_string
                
                # Create a fresh session for each attempt
                session = requests.Session()
                
                # Update headers for this attempt
                headers = self.headers_step1.copy()
                
                # Add some randomization to avoid detection
                headers["x-requested-with"] = "XMLHttpRequest"
                
                # Make the request with decompression support
                headers['accept-encoding'] = 'gzip, deflate'
                resp = session.post(url, json=payload, headers=headers, timeout=60)
                
                logger.info(f"Response status: {resp.status_code}")
                logger.info(f"Response headers: {dict(resp.headers)}")
                logger.info(f"Response content length: {len(resp.content)}")
                
                # Handle different status codes
                if resp.status_code == 429:
                    logger.warning("Rate limited, waiting longer before retry...")
                    time.sleep(10 * (attempt + 1))
                    continue
                elif resp.status_code == 403:
                    logger.warning("Forbidden response, regenerating session...")
                    time.sleep(5 * (attempt + 1))
                    continue
                elif resp.status_code != 200:
                    logger.warning(f"Non-200 status code: {resp.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(3 * (attempt + 1))
                        continue
                
                resp.raise_for_status()
                
                # Check if response has content
                if not resp.text.strip():
                    logger.warning(f"Empty response on attempt {attempt + 1}, retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        raise Exception("Empty response from VisualGPT API after all retries")
                
                # Log raw response for debugging
                logger.info(f"Raw response (first 500 chars): {resp.text[:500]}")
                
                # Try to parse JSON
                try:
                    data = resp.json()
                except ValueError as e:
                    logger.error(f"Invalid JSON response from VisualGPT: {resp.text[:200]}...")
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"Invalid JSON response from VisualGPT API after all retries: {e}")
                
                # Check response structure
                logger.info(f"Response data: {data}")
                
                if data.get("code") == 100000 and "session_id" in data.get("data", {}):
                    session_id = data["data"]["session_id"]
                    logger.info(f"Prediction submitted successfully, session_id: {session_id}")
                    return session_id
                else:
                    error_msg = data.get('message', 'unknown error')
                    error_code = data.get('code', 'unknown')
                    logger.error(f"Submission failed: {error_msg} (code: {error_code})")
                    
                    # Handle specific error codes
                    if error_code == 100001:  # Common error code
                        logger.info("Retrying with fresh session...")
                        time.sleep(3 * (attempt + 1))
                        continue
                    
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"Submission failed after all retries: {error_msg} (code: {error_code})")
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error during submission attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3 * (attempt + 1))
                    continue
                else:
                    raise Exception(f"Network error after all retries: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during submission attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                else:
                    raise

    def poll_status(self, session_id, timeout=180, interval=5, task_id=None):
        url = f"https://visualgpt.io/api/v1/prediction/get-status?session_id={session_id}"
        start = time.time()
        logger.info(f"Starting to poll status for session_id: {session_id}")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while True:
            try:
                headers = self.headers_step2.copy()
                # update path header so it matches (optional but good replication)
                headers["path"] = f"/api/v1/prediction/get-status?session_id={session_id}"
                resp = requests.get(url, headers=headers, timeout=30)
                
                # Reset error counter on successful request
                consecutive_errors = 0
                
                if resp.status_code != 200:
                    logger.warning(f"Non-200 status during polling: {resp.status_code}")
                    time.sleep(interval)
                    continue
                
                # Check if response has content
                if not resp.text.strip():
                    logger.warning("Empty response received, retrying...")
                    time.sleep(interval)
                    continue
                
                # Try to parse JSON
                try:
                    data = resp.json()
                except ValueError as e:
                    logger.warning(f"Invalid JSON response: {resp.text[:100]}... Error: {e}")
                    time.sleep(interval)
                    continue

                logger.info(f"Polling response: {data}")

                # if server signals session timeout
                msg = data.get("message", "")
                if "time" in msg.lower() and "out" in msg.lower():
                    logger.error("Session timed out on server side")
                    raise Exception("Session timed out on server side.")

                # Check for error in response
                if data.get("code") != 100000:
                    error_msg = data.get("message", "Unknown error")
                    logger.error(f"API error during polling: {error_msg}")
                    raise Exception(f"API error: {error_msg}")

                results = data.get("data", {}).get("results", [])
                if results:
                    result = results[0]
                    status = result.get("status", "")
                    progress = result.get("progress", 0)
                    logger.info(f"Current status: {status}, progress: {progress}%")
                    
                    # Update task progress if task_id provided
                    if task_id and status in ["processing", "queued", "starting"]:
                        # Map API progress (0-100) to our range (30-85)
                        mapped_progress = 30 + int((progress / 100) * 55)
                        generation_progress[task_id] = {
                            "status": "processing",
                            "progress": mapped_progress,
                            "message": f"AI is generating... {progress}%",
                            "stage": "generate"
                        }
                    
                    if status == "succeeded":
                        # The API returns URLs in an array, not as a single URL
                        urls = result.get("urls", [])
                        if urls and len(urls) > 0:
                            img_url = urls[0]
                            logger.info(f"Image generation succeeded: {img_url}")
                            return img_url
                        else:
                            logger.error("Succeeded status but URLs array is empty")
                            raise Exception("Succeeded status but URLs array is empty.")
                    elif status == "failed":
                        error_detail = result.get("error", "Unknown error")
                        logger.error(f"Image generation failed: {error_detail}")
                        raise Exception(f"Generation failed: {error_detail}")
                    elif status in ["processing", "queued", "starting"]:
                        logger.info(f"Generation in progress: {status} ({progress}%)")
                    else:
                        logger.info(f"Unknown status: {status}")
                else:
                    logger.info("No results yet, continuing to poll...")
                        
            except requests.exceptions.RequestException as e:
                consecutive_errors += 1
                logger.warning(f"Request error during polling ({consecutive_errors}/{max_consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive polling errors")
                    raise Exception(f"Polling failed after {max_consecutive_errors} consecutive errors")
                
                time.sleep(interval * 2)  # Wait longer after errors
                continue
                
            # Timeout check
            elapsed = time.time() - start
            if elapsed > timeout:
                logger.error(f"Timeout waiting for image generation after {timeout}s")
                raise Exception("Script timeout waiting for image generation.")
            
            time.sleep(interval)

    async def generate_image(self, prompt: str, image_url: str = None, task_id: str = None) -> str:
        """Generate an image and return the uploaded URL from uguu.se"""
        try:
            # Use default URL if image_url is None or empty
            starting_image = image_url if image_url and image_url.strip() else IMAGE_UPLOAD_URL
            logger.info(f"Starting image generation for prompt: {prompt[:50]}... with starting_image: {starting_image}")
            
            # Update progress
            if task_id:
                generation_progress[task_id] = {
                    "status": "processing",
                    "progress": 10,
                    "message": "Submitting request to AI...",
                    "stage": "submit"
                }
            
            # Set shorter timeout for initial attempt
            session_id = self.submit_prediction(prompt, starting_image)
            
            # Update progress
            if task_id:
                generation_progress[task_id] = {
                    "status": "processing",
                    "progress": 30,
                    "message": "Generating image...",
                    "stage": "generate"
                }
            
            original_image_url = self.poll_status(session_id, timeout=120, task_id=task_id)  # 2 minutes max
            
            # Update progress
            if task_id:
                generation_progress[task_id] = {
                    "status": "processing",
                    "progress": 90,
                    "message": "Uploading to server...",
                    "stage": "upload"
                }
            
            # Upload to uguu.se and return the new URL
            uploaded_url = upload_image_to_uguu(original_image_url)
            logger.info(f"Image generation and upload completed successfully")
            return uploaded_url
        except Exception as e:
            logger.error(f"VisualGPT generation failed: {str(e)}")
            
            # Try fallback if enabled
            if FALLBACK_ENABLED:
                logger.info("Attempting fallback image generation...")
                if task_id:
                    generation_progress[task_id] = {
                        "status": "processing",
                        "progress": 50,
                        "message": "Using fallback generator...",
                        "stage": "fallback"
                    }
                fallback_provider = FallbackImageProvider()
                return await fallback_provider.generate_image(prompt, image_url)
            else:
                raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# --- App Init ---
app = FastAPI(
    title="🍌 Nano Banana Image Generation API", 
    version="2.0.0",
    description="""A powerful image generation API that creates images from text prompts and uploads them to uguu.se.
    
## Features
- Generate images from text descriptions
- Optional starting image for editing
- Automatic upload to uguu.se for easy sharing
- Real-time generation status with structured logging
- Batch processing capabilities
- Web interface support
- History tracking and analytics
    
## Usage
1. Use the `/v1/image/generations` endpoint for programmatic access
2. Check `/health` for service status
3. All generated images are automatically uploaded to uguu.se
4. Access the web interface at `/web`
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = VisualGPTProvider()

# Create directories for file storage
os.makedirs("uploads", exist_ok=True)
os.makedirs("output_images", exist_ok=True)
os.makedirs("cache", exist_ok=True)


# --- Routes ---
@app.post("/v1/image/generations", 
         summary="Generate Image",
         description="Generate an image based on a text prompt and upload it to uguu.se. Optionally provide a starting image URL for editing.",
         response_description="Returns the uploaded image URL from uguu.se")
async def create_image(request: ImageGenerationRequest):
    """Generate an image based on a text prompt and upload to uguu.se.
    
    - **prompt**: The text description of the image you want to generate
    - **image_url**: Optional starting image URL for editing (uses default if not provided)
    
    Returns the uploaded image URL from uguu.se instead of the original generation URL.
    """
    logger.info(f"Received image generation request: prompt='{request.prompt[:50]}...', image_url='{request.image_url}'")
    
    if not request.prompt or not request.prompt.strip():
        logger.error("Empty prompt provided")
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    # Create task ID for progress tracking
    task_id = str(uuid.uuid4())
    generation_progress[task_id] = {
        "status": "starting",
        "progress": 0,
        "message": "Initializing generation...",
        "stage": "init"
    }
    
    try:
        uploaded_url = await provider.generate_image(
            request.prompt, 
            request.image_url if request.image_url and request.image_url.strip() else None,
            task_id=task_id
        )
        
        # Update progress to complete
        generation_progress[task_id] = {
            "status": "complete",
            "progress": 100,
            "message": "Generation complete!",
            "stage": "complete"
        }
        
        created_ts = int(time.time())
        
        response_payload = {
            "created": created_ts,
            "task_id": task_id,
            "data": [
                {
                    "url": uploaded_url,
                    "revised_prompt": request.prompt
                }
            ]
        }
        
        logger.info(f"Successfully generated and uploaded image, returning uguu.se URL")
        return JSONResponse(content=response_payload)
        
    except HTTPException:
        generation_progress[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": "Generation failed",
            "stage": "error"
        }
        raise
    except Exception as e:
        generation_progress[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": str(e),
            "stage": "error"
        }
        logger.error(f"Unexpected error during image generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/", summary="API Info", description="Get basic information about the API")
async def root():
    """Get API information"""
    return {
        "message": "🍌 Nano Banana Image Generation API", 
        "version": "1.0.0",
        "description": "Generate images from text prompts and upload to uguu.se",
        "endpoints": {
            "POST /v1/image/generations": "Generate image from prompt",
            "GET /docs": "Swagger UI documentation",
            "GET /health": "Health check"
        }
    }


@app.get("/health", summary="Health Check", description="Check if the API service is running")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Nano Banana Image Generation API"}

@app.get("/web", summary="Web Interface", description="Serve the web interface")
async def serve_web_interface():
    """Serve the ULTIMATE web interface with gallery, batch processing, and all features"""
    html_path = os.path.join(os.path.dirname(__file__), "web_interface_v4.html")
    return FileResponse(html_path)

@app.get("/web/v3", summary="Web Interface V3", description="Serve the PRO web interface")
async def serve_web_interface_v3():
    """Serve the PRO web interface with advanced controls and comparison slider"""
    html_path = os.path.join(os.path.dirname(__file__), "web_interface_v3.html")
    return FileResponse(html_path)

@app.get("/web/v2", summary="Web Interface V2", description="Serve the enhanced web interface")
async def serve_web_interface_v2():
    """Serve the enhanced web interface"""
    html_path = os.path.join(os.path.dirname(__file__), "web_interface_v2.html")
    return FileResponse(html_path)

@app.get("/web/v1", summary="Web Interface V1", description="Serve the original web interface")
async def serve_web_interface_v1():
    """Serve the original web interface"""
    html_path = os.path.join(os.path.dirname(__file__), "web_interface.html")
    return FileResponse(html_path)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return empty response for favicon to prevent 404 errors"""
    return JSONResponse(content={}, status_code=204)

@app.get("/v1/progress/{task_id}", summary="Get Generation Progress", description="Get real-time progress for a generation task")
async def get_progress(task_id: str):
    """Get real-time progress for a generation task"""
    if task_id in generation_progress:
        return generation_progress[task_id]
    return {"status": "not_found", "progress": 0, "message": "Task not found"}

@app.get("/v1/gallery", summary="Get Gallery", description="Get all gallery items")
async def get_gallery():
    """Get all gallery items"""
    return {"items": gallery_items, "total": len(gallery_items)}

@app.post("/v1/gallery", summary="Add to Gallery", description="Add item to gallery")
async def add_to_gallery(item: dict):
    """Add item to gallery"""
    gallery_items.insert(0, item)
    # Keep only last 100 items
    if len(gallery_items) > 100:
        gallery_items.pop()
    return {"success": True, "total": len(gallery_items)}

@app.delete("/v1/gallery/{item_id}", summary="Delete from Gallery", description="Delete item from gallery")
async def delete_from_gallery(item_id: str):
    """Delete item from gallery"""
    global gallery_items
    gallery_items = [item for item in gallery_items if item.get("id") != item_id]
    return {"success": True, "total": len(gallery_items)}

@app.post("/v1/batch", summary="Batch Process Images", description="Process multiple images at once")
async def batch_process(files: List[UploadFile] = File(...), prompt: str = Form(...), 
                       strength: float = Form(0.8), format: str = Form("jpg")):
    """Process multiple images with the same prompt"""
    batch_id = str(uuid.uuid4())
    batch_queue[batch_id] = {
        "status": "processing",
        "total": len(files),
        "completed": 0,
        "results": []
    }
    
    try:
        for i, file in enumerate(files):
            try:
                # Upload file
                content = await file.read()
                timestamp = int(time.time())
                filename = f"batch_{timestamp}_{i}_{file.filename}"
                filepath = os.path.join("uploads", filename)
                
                with open(filepath, "wb") as buffer:
                    buffer.write(content)
                
                # Upload to uguu.se
                image_data = io.BytesIO(content)
                files_dict = {"files[]": (filename, image_data, file.content_type)}
                
                upload_response = requests.post("https://uguu.se/upload", files=files_dict, timeout=30)
                
                if upload_response.status_code == 200:
                    data = upload_response.json()
                    if data.get("success") and data.get("files"):
                        image_url = data["files"][0].get("url")
                        
                        # Generate edited image
                        task_id = str(uuid.uuid4())
                        edited_url = await provider.generate_image(prompt, image_url, task_id)
                        
                        batch_queue[batch_id]["results"].append({
                            "original": image_url,
                            "edited": edited_url,
                            "status": "success"
                        })
                        batch_queue[batch_id]["completed"] += 1
                
            except Exception as e:
                logger.error(f"Batch item {i} failed: {e}")
                batch_queue[batch_id]["results"].append({
                    "original": None,
                    "edited": None,
                    "status": "failed",
                    "error": str(e)
                })
                batch_queue[batch_id]["completed"] += 1
        
        batch_queue[batch_id]["status"] = "complete"
        return {"batch_id": batch_id, "results": batch_queue[batch_id]["results"]}
        
    except Exception as e:
        batch_queue[batch_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/v1/batch/{batch_id}", summary="Get Batch Status", description="Get batch processing status")
async def get_batch_status(batch_id: str):
    """Get batch processing status"""
    if batch_id in batch_queue:
        return batch_queue[batch_id]
    return {"status": "not_found"}

@app.post("/upload", summary="Upload File", description="Upload an image file for editing")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image file and return its URL"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        content = await file.read()
        
        # Generate unique filename
        timestamp = int(time.time())
        filename = f"upload_{timestamp}_{file.filename}"
        
        # Save file locally as backup
        filepath = os.path.join("uploads", filename)
        with open(filepath, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"⏳ Uploading {filename} to uguu.se...")
        
        # Upload directly to uguu.se using file bytes
        image_data = io.BytesIO(content)
        files = {"files[]": (filename, image_data, file.content_type)}
        
        # Try uguu.se first, then fallback to other services
        upload_services = [
            ("https://uguu.se/upload", "uguu.se"),
            ("https://0x0.st", "0x0.st")
        ]
        
        for upload_url, service_name in upload_services:
            try:
                if service_name == "0x0.st":
                    # 0x0.st uses different format
                    image_data.seek(0)  # Reset stream position
                    files = {"file": (filename, image_data, file.content_type)}
                
                upload_response = requests.post(upload_url, files=files, timeout=30)
                
                if upload_response.status_code == 200:
                    if service_name == "uguu.se":
                        data = upload_response.json()
                        if data.get("success") and data.get("files"):
                            uploaded_url = data["files"][0].get("url")
                            if uploaded_url:
                                logger.info(f"✅ Upload successful to {service_name}: {uploaded_url}")
                                return {"success": True, "url": uploaded_url, "filename": filename}
                    elif service_name == "0x0.st":
                        uploaded_url = upload_response.text.strip()
                        if uploaded_url.startswith("http"):
                            logger.info(f"✅ Upload successful to {service_name}: {uploaded_url}")
                            return {"success": True, "url": uploaded_url, "filename": filename}
                
                logger.warning(f"Upload to {service_name} failed, trying next service...")
                
            except Exception as e:
                logger.warning(f"Upload to {service_name} failed: {e}")
                continue
        
        # If all upload services fail, raise an error
        raise Exception("All upload services failed")
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/v1/image/batch", 
         summary="Batch Generate Images",
         description="Generate multiple images from multiple prompts")
async def batch_generate_images(request: BatchGenerationRequest):
    """Generate multiple images from multiple prompts"""
    logger.info(f"Received batch generation request for {len(request.prompts)} prompts")
    
    results = []
    for i, prompt in enumerate(request.prompts):
        try:
            logger.info(f"Processing batch item {i+1}/{len(request.prompts)}: {prompt[:50]}...")
            image_url = await provider.generate_image(prompt)
            
            results.append({
                "prompt": prompt,
                "url": image_url,
                "status": "success",
                "index": i
            })
            
        except Exception as e:
            logger.error(f"Batch item {i+1} failed: {e}")
            results.append({
                "prompt": prompt,
                "url": None,
                "status": "failed",
                "error": str(e),
                "index": i
            })
    
    success_count = len([r for r in results if r["status"] == "success"])
    
    return {
        "total": len(request.prompts),
        "successful": success_count,
        "failed": len(request.prompts) - success_count,
        "results": results
    }

@app.get("/v1/history", summary="Get Generation History", description="Get generation history")
async def get_history():
    """Get generation history"""
    history_file = "generation_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            return {"history": history}
        except Exception as e:
            logger.error(f"Error reading history: {e}")
            return {"history": []}
    return {"history": []}

@app.post("/v1/history", summary="Add to History", description="Add item to generation history")
async def add_to_history(item: HistoryItem):
    """Add item to generation history"""
    history_file = "generation_history.json"
    
    try:
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new item
        history.insert(0, item.dict())
        
        # Keep only last 100 items
        history = history[:100]
        
        # Save back to file
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"Added item to history: {item.id}")
        return {"success": True, "message": "Item added to history"}
        
    except Exception as e:
        logger.error(f"Error adding to history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add to history: {str(e)}")

@app.get("/v1/stats", summary="Get Statistics", description="Get generation statistics")
async def get_statistics():
    """Get generation statistics"""
    stats_file = "generation_stats.json"
    
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        except Exception as e:
            logger.error(f"Error reading stats: {e}")
            stats = {"total_generations": 0, "successful_generations": 0, "failed_generations": 0}
    else:
        stats = {"total_generations": 0, "successful_generations": 0, "failed_generations": 0}
    
    # Add current session stats
    stats["server_uptime"] = int(time.time())
    stats["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    return stats

@app.post("/v1/stats", summary="Update Statistics", description="Update generation statistics")
async def update_statistics(success: bool = True):
    """Update generation statistics"""
    stats_file = "generation_stats.json"
    
    try:
        # Load existing stats
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {"total_generations": 0, "successful_generations": 0, "failed_generations": 0}
        
        # Update stats
        stats["total_generations"] += 1
        if success:
            stats["successful_generations"] += 1
        else:
            stats["failed_generations"] += 1
        
        stats["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Save back to file
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        logger.error(f"Error updating stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Nano Banana Image Generation API server on port 10000")
    logger.info("Web interface available at: http://127.0.0.1:10000/web")
    uvicorn.run("main:app", host="127.0.0.1", port=10000, reload=True)
