# 🩺 Predicare VoiceBot - AI Doctor with Voice & Vision

An AI-powered medical assistant that combines voice recognition, image analysis, and text-to-speech to provide medical guidance through natural conversation.

![AI Doctor Demo](https://img.shields.io/badge/Status-Working-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange)

## 🌟 Features

- 🎤 **Voice Input**: Record symptoms and medical concerns
- 🧠 **AI Analysis**: Intelligent medical assessment using Groq LLM
- 📸 **Image Analysis**: Upload medical images for visual diagnosis
- 🔊 **Voice Output**: AI doctor responds with natural speech
- 🌐 **Web Interface**: User-friendly Gradio web application
- 📱 **Cross-Platform**: Works on any device with internet access

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- GROQ API Key
- ElevenLabs API Key

### Installation

1. Clone the repository:
```bash
git clone git@github.com:Pratik00531/Predicare-VoiceBot.git
cd Predicare-VoiceBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
python gradio_app_simple.py
```

## 🔧 Configuration

Create a `.env` file with the following:

```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

## 📁 Project Structure

```
├── brain_of_the_doctor.py     # Image analysis and AI reasoning
├── voice_of_the_patient.py    # Speech-to-text processing
├── voice_of_the_doctor.py     # Text-to-speech generation
├── gradio_app_simple.py       # Main web application (recommended)
├── gradio_app_optimized.py    # Alternative optimized version
├── gradio_app.py              # Original version
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not in repo)
└── README.md                  # This file
```

## 🎯 How It Works

1. **Record Symptoms**: User describes their medical concerns via voice
2. **Transcription**: Speech is converted to text using Groq Whisper
3. **AI Analysis**: Text is analyzed by LLM for medical assessment
4. **Image Processing**: Optional image upload for visual analysis
5. **Response Generation**: AI provides medical guidance and recommendations
6. **Voice Output**: Response is converted back to speech using ElevenLabs

## 🛡️ Important Disclaimers

⚠️ **This application is for educational purposes only**
- Not a substitute for professional medical advice
- Always consult qualified healthcare professionals
- Do not use for emergency medical situations

## 🧪 Technology Stack

- **AI/ML**: Groq LLM, Whisper (Speech-to-Text)
- **Voice**: ElevenLabs Text-to-Speech
- **Frontend**: Gradio Web UI
- **Backend**: Python
- **APIs**: RESTful API integration

## 📊 API Usage

### Speech-to-Text
```python
from voice_of_the_patient import transcribe_with_groq

result = transcribe_with_groq(
    audio_filepath="recording.wav",
    GROQ_API_KEY="your_key",
    stt_model="whisper-large-v3"
)
```

### Medical Analysis
```python
from brain_of_the_doctor import analyze_image_with_query

response = analyze_image_with_query(
    query="What do you see in this image?",
    model="llama-3.1-8b-instant",
    encoded_image=base64_image
)
```

### Text-to-Speech
```python
from voice_of_the_doctor import text_to_speech_with_elevenlabs

audio_file = text_to_speech_with_elevenlabs(
    input_text="Your medical assessment...",
    output_filepath="response.mp3"
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for AI/ML infrastructure
- [ElevenLabs](https://elevenlabs.io/) for voice synthesis
- [Gradio](https://gradio.app/) for the web interface
- Open source medical AI research community

---

**Made with ❤️ for educational healthcare AI**
