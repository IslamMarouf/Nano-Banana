# 🍌 Nano Banana Image Generator

A console application for creating and editing images using AI.

## Features

- **Create new images** from text prompts
- **Edit existing images** with text descriptions
- **Interactive console interface**
- **Automatic image saving** to `output_images` folder
- **Progress indicators** and status messages

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the console app:
```bash
python app.py
```

3. Choose your option:
   - **Create**: Generate a new image from a text prompt
   - **Edit**: Modify an existing image (local file or URL) with a text prompt

4. Generated images are automatically saved to the `output_images` folder

## File Structure

- `app.py` - Main console application
- `main.py` - FastAPI server with image generation logic
- `utils.py` - Helper functions for image operations
- `output_images/` - Folder where generated images are saved
- `requirements.txt` - Python dependencies