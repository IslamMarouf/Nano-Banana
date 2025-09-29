# 🍌 Nano Banana Image Generator

A comprehensive AI-powered image generation and editing application with console, web API, mobile, and PWA interfaces.

## ✨ Features

### 🎯 Core Functionality
- **Create new images** from text prompts using AI
- **Edit existing images** with text descriptions
- **Multiple image formats** (JPG, PNG, WebP, AVIF, TIFF, BMP, GIF)
- **Configurable resolution** and quality settings
- **Automatic image saving** to `output_images` folder

### 🚀 Enhanced User Experience
- **Beautiful progress bars** with Rich library
- **Interactive settings menu** for customization
- **Persistent configuration** management
- **Enhanced error handling** with detailed messages
- **Modern console interface** with colors and formatting
- **Web interface** with drag & drop support
- **Mobile-responsive design** for all devices

### 🤖 AI-Powered Features
- **Smart prompt optimization** with AI suggestions
- **Advanced image editing** (inpainting, outpainting, style transfer)
- **Content filtering** and NSFW detection
- **Intelligent style variations** generation
- **Negative prompt suggestions** for better results

### 🔗 Integration & Export
- **Webhook support** for external integrations
- **API integrations** (Discord, Slack, Telegram, Dropbox, Google Drive)
- **Multiple export formats** with optimization
- **Social media sharing** links and optimization
- **Batch processing** for multiple images

### 📱 Mobile & PWA
- **Progressive Web App** (PWA) support
- **Mobile-first design** with touch gestures
- **Offline functionality** with service workers
- **Push notifications** for completed generations
- **Camera integration** for mobile devices
- **Voice commands** for hands-free operation

### 🛡️ Safety & Security
- **Content filtering** system
- **NSFW detection** and blocking
- **Hate speech** pattern recognition
- **Age-inappropriate content** detection
- **Legal compliance** checking

## 🚀 Quick Start

### Option 1: Automatic Installation
```bash
python install.py
```

### Option 2: Manual Installation
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the console app:
```bash
python app.py
```

3. Or start the API server:
```bash
python main.py
```

## 📖 Usage

### Console Application
1. Run `python app.py`
2. Choose your option:
   - **Create**: Generate a new image from a text prompt
   - **Edit**: Modify an existing image (local file or URL)
   - **Settings**: Configure application preferences
   - **Exit**: Close the application

### Settings Menu
Access the settings menu to configure:
- **Output Format**: Choose between JPG, PNG, WebP
- **Resolution**: Set image dimensions (512x512, 1024x1024, 2048x2048)
- **Progress Display**: Toggle progress bars on/off
- **Fallback Mode**: Enable/disable fallback image generation
- **Quality Settings**: Adjust image quality preferences

### API Server
Start the FastAPI server with `python main.py` and access:
- **POST /v1/image/generations** - Generate images
- **GET /health** - Health check
- **GET /docs** - Interactive API documentation

## 📁 File Structure

### Core Files
- `app.py` - Enhanced console application with Rich UI
- `main.py` - FastAPI server with image generation logic
- `utils.py` - Helper functions with format detection and error handling
- `config_manager.py` - Configuration management system
- `config.json` - Persistent settings (auto-generated)
- `install.py` - Automated installation script
- `demo.py` - Feature demonstration script
- `output_images/` - Generated images storage
- `requirements.txt` - Python dependencies

### Advanced Features
- `prompt_optimizer.py` - AI-powered prompt optimization system
- `advanced_image_editor.py` - Advanced image editing with style transfer
- `content_filter.py` - Content filtering and NSFW detection
- `api_integrations.py` - Webhook support and external API integrations
- `export_sharing.py` - Multiple export formats and social sharing
- `mobile_pwa.py` - Mobile app and Progressive Web App support
- `demo_advanced_features.py` - Comprehensive advanced features demo

### Web Interface
- `web_interface.html` - Modern web interface with drag & drop
- `batch_processor.py` - Batch image processing system
- `cache_manager.py` - Image caching system
- `analytics_dashboard.py` - Usage analytics and history tracking

## 🎨 New Features in Detail

### Visual Progress Bars
- Real-time progress indicators during image generation
- Configurable progress display (can be disabled)
- Beautiful animations with Rich library

### Configuration Management
- Persistent settings saved to `config.json`
- Easy-to-use settings menu in console app
- Support for different output formats and resolutions
- Configurable UI preferences

### Enhanced Error Handling
- Specific error messages for different failure types
- Better network error handling with timeouts
- Graceful fallback to placeholder images
- Detailed error reporting with suggestions

### Multiple Image Formats
- Automatic format detection from URLs
- Support for JPG, PNG, WebP formats
- Configurable default output format
- Proper MIME type handling

## 🔧 Configuration

The application uses `config.json` for persistent settings:

```json
{
  "default_settings": {
    "output_format": "jpg",
    "resolution": "1024x1024",
    "quality": "high"
  },
  "ui_settings": {
    "show_progress": true,
    "color_theme": "default"
  },
  "advanced_settings": {
    "fallback_enabled": true,
    "cache_images": true
  }
}
```

## 🎯 Demo

### Basic Features Demo
Run the basic features demo:
```bash
python demo.py
```

### Advanced Features Demo
Run the comprehensive advanced features demo:
```bash
python demo_advanced_features.py
```

### Individual Feature Demos
- `python prompt_optimizer.py` - AI prompt optimization
- `python advanced_image_editor.py` - Advanced image editing
- `python content_filter.py` - Content filtering and safety
- `python api_integrations.py` - API integrations and webhooks
- `python export_sharing.py` - Export and sharing options
- `python mobile_pwa.py` - Mobile and PWA features

## 🛠️ Development

### Adding New Features
1. Update `config_manager.py` for new settings
2. Modify `app.py` for console interface changes
3. Update `utils.py` for utility functions
4. Test with `demo.py`

### API Integration
The app uses VisualGPT.io's Nano Banana model for image generation with automatic fallback to placeholder services.

## 📝 Requirements

- Python 3.8+
- Internet connection for AI image generation
- Dependencies listed in `requirements.txt`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python demo.py`
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.