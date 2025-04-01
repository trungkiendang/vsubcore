# VSubCore

VSubCore is a powerful speech recognition tool that converts video/audio files to text and generates SRT subtitles. It supports multiple languages and provides fast, efficient processing.

## Features

- Convert video/audio files to text
- Support for multiple languages
- Generate SRT subtitles
- Fast and efficient processing
- Simple command-line interface

## Installation

```bash
pip install vsubcore
```

## Usage

Basic usage:

```bash
vsub-nolog.py source_path [-o output] [-S stt-language]
```

Parameters:
- `source_path`: Path to the video/audio file
- `-o, --output`: Output directory for subtitle file (optional)
- `-S, --stt-language`: Language for speech recognition (default: "en")

Example:
```bash
vsub-nolog.py video.mp4 -o subtitles.srt -S en
```

## Supported Languages

VSubCore supports a wide range of languages including:
- English (en)
- Vietnamese (vi)
- Japanese (ja)
- Korean (ko)
- Chinese (zh-CN, zh-TW)
- And many more...

For a complete list of supported languages, please refer to the [language codes documentation](docs/index.html#supported-languages).

## Requirements

- Python 3.6 or higher
- FFmpeg
- Google Speech API key

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Google Speech API for speech recognition
- FFmpeg for audio processing 