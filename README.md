# Novel Translator

A FastAPI-based web application for translating novels and individual chapters using ONNX machine learning models. Features emotion preservation, glossary management for consistency, and batch processing capabilities.

## Features

### Core Functionality
- **Chapter Translation**: Translate individual chapters or text passages
- **Novel Translation**: Batch translate entire novels from ZIP archives
- **Emotion Preservation**: Maintains emotional tone using emotion_quantized.onnx model
- **Glossary Management**: Ensures consistency of character names and terms across chapters
- **Language Detection**: Automatically detects source language
- **Progress Tracking**: Real-time progress updates for batch translations

### Technical Features
- FastAPI backend with async support
- ONNX runtime integration for ML models
- Modern Bootstrap-based responsive UI
- File upload with drag-and-drop support
- ZIP file processing and creation
- Side-by-side translation comparison
- Download functionality for translated content

## Installation

1. **Clone the repository** (or create the project structure):
```bash
mkdir novel_translator
cd novel_translator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up ONNX models**:
   - Place your ONNX models in the `models/` directory:
     - `translation_mul2en_quantized.onnx` - For translating multiple languages to English
     - `translation_en2mul_quantized.onnx` - For translating English to multiple languages  
     - `emotion_quantized.onnx` - For emotion preservation analysis

4. **Run the application**:
```bash
cd novel_translator
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

### Chapter Translation

1. Navigate to the **Chapter Translation** page
2. Either:
   - Upload a text file (.txt), or
   - Paste text directly into the text area
3. Select your target language
4. Click "Translate Chapter"
5. View side-by-side comparison of original and translated text
6. Download the translated chapter

### Novel Translation

1. Navigate to the **Novel Translation** page  
2. Upload a ZIP file containing your novel chapters as .txt files
3. Select your target language
4. Click "Start Novel Translation"
5. Monitor progress as chapters are processed
6. Download the translated novel as a ZIP file

### ZIP File Structure

For novel translation, organize your chapters in a ZIP file like this:
```
novel.zip
├── Chapter_01.txt
├── Chapter_02.txt
├── Chapter_03.txt
└── ...
```

- Files are processed alphabetically
- Use consistent naming (e.g., Chapter_01, Chapter_02, etc.)
- Only .txt and .text files are processed
- Maximum file size: 100MB

## API Endpoints

- `GET /` - Home page
- `GET /chapter` - Chapter translation interface  
- `GET /novel` - Novel translation interface
- `POST /translate-chapter` - Process chapter translation
- `POST /translate-novel` - Process novel translation
- `POST /download-chapter` - Download translated chapter

## Project Structure

```
novel_translator/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── chapter_translate.py    # Single chapter translation logic
│   ├── novel_translate.py      # Batch novel translation logic
│   ├── glossary.py             # Glossary management for consistency
│   ├── detect_lang.py          # Language detection utilities
│   ├── emotion.py              # Emotion preservation using ONNX
│   └── utils.py                # File handling and utility functions
├── static/
│   ├── style.css               # Custom CSS styles
│   └── script.js               # JavaScript functionality
├── templates/
│   ├── base.html               # Base template
│   ├── index.html              # Home page
│   ├── chapter.html            # Chapter translation page
│   └── novel.html              # Novel translation page
├── models/                     # Directory for ONNX models
│   ├── translation_mul2en_quantized.onnx
│   ├── translation_en2mul_quantized.onnx
│   └── emotion_quantized.onnx
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Supported Languages

Currently supports translation between:
- English
- Spanish
- French  
- German
- Italian
- Portuguese
- Japanese
- Korean
- Chinese
- Russian

## Technical Details

### ONNX Model Integration

The application uses three ONNX models:

1. **translation_mul2en_quantized.onnx**: Translates from various languages to English
2. **translation_en2mul_quantized.onnx**: Translates from English to various languages  
3. **emotion_quantized.onnx**: Analyzes and preserves emotional content

### Glossary System

The glossary system ensures consistency across chapters by:
- Tracking character names and important terms
- Maintaining consistent translations throughout the novel
- Building context from multiple chapters
- Providing fallback translations when needed

### Error Handling

The application includes robust error handling for:
- File upload validation
- ONNX model loading failures
- Translation timeouts
- Corrupt ZIP files
- Encoding issues

## Development

### Running in Development Mode

```bash
cd novel_translator
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

The application includes comprehensive error handling and validation. For production use, consider adding:
- Unit tests for translation functions
- Integration tests for file processing
- Performance tests for large novels
- Security tests for file uploads

## Production Deployment

For production deployment:

1. Set up a proper WSGI server (gunicorn)
2. Configure nginx for static file serving  
3. Set up proper logging
4. Implement rate limiting
5. Add authentication if needed
6. Set up monitoring and health checks

## Performance Considerations

- ONNX models are loaded once and reused
- Large novels are processed in chunks
- Temporary files are cleaned up automatically
- Progress tracking prevents timeout issues
- File size limits prevent resource exhaustion

## Security Features

- File type validation
- File size limits
- Path traversal prevention
- Input sanitization
- Temporary file cleanup

## License

This project is open source. Please ensure you have proper licenses for any ONNX models you use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues or questions:
1. Check the troubleshooting section below
2. Review the error logs
3. Open an issue with detailed information

## Troubleshooting

### Common Issues

1. **ONNX models not found**: Ensure models are placed in the `models/` directory with correct names
2. **Translation takes too long**: Large files are processed in chunks; check server resources
3. **File upload fails**: Check file size limits and supported formats
4. **ZIP extraction errors**: Ensure ZIP file is not corrupted and contains .txt files

### Debug Mode

Run with debug logging:
```bash
python -m uvicorn app.main:app --reload --log-level debug
```