"""
FastAPI Backend for Predicare VoiceBot
Provides REST API endpoints for AI Doctor functionality
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
import base64
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import your AI Doctor modules
from brain_of_the_doctor import analyze_image_with_query, encode_image
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

app = FastAPI(
    title="Predicare VoiceBot API",
    description="AI Doctor with Voice & Vision - REST API Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for TypeScript frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TranscriptionResponse(BaseModel):
    transcription: str
    success: bool
    message: str

class AnalysisRequest(BaseModel):
    query: str
    image_base64: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis: str
    success: bool
    message: str

class SynthesisRequest(BaseModel):
    text: str

class SynthesisResponse(BaseModel):
    audio_url: str
    success: bool
    message: str

class ConsultationRequest(BaseModel):
    query: Optional[str] = None
    image_base64: Optional[str] = None

class ConsultationResponse(BaseModel):
    transcription: Optional[str] = None
    analysis: str
    audio_url: Optional[str] = None
    success: bool
    message: str

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Predicare VoiceBot API is running!",
        "version": "1.0.0",
        "endpoints": [
            "/transcribe",
            "/analyze", 
            "/synthesize",
            "/consultation",
            "/docs"
        ]
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "groq": bool(os.environ.get("GROQ_API_KEY")),
            "elevenlabs": bool(os.environ.get("ELEVENLABS_API_KEY"))
        }
    }

# Speech-to-Text endpoint
@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    """Convert audio to text using Groq Whisper"""
    
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be audio format")
    
    try:
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        # Transcribe using Groq
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        
        transcription = transcribe_with_groq(
            audio_filepath=temp_audio_path,
            GROQ_API_KEY=groq_api_key,
            stt_model="whisper-large-v3"
        )
        
        # Clean up temp file
        os.unlink(temp_audio_path)
        
        return TranscriptionResponse(
            transcription=transcription,
            success=True,
            message="Audio transcribed successfully"
        )
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_audio_path' in locals():
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# Medical Analysis endpoint
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_medical_query(request: AnalysisRequest):
    """Analyze medical query with optional image"""
    
    try:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        
        # System prompt for medical analysis
        system_prompt = """You are a medical AI assistant for educational purposes only. 
        Based on the patient's description, provide general medical information and suggest when to seek professional care. 
        Always remind patients that this is not a substitute for professional medical advice."""
        
        full_query = f"{system_prompt}\n\nPatient describes: {request.query}"
        
        # If image is provided, try vision analysis first
        if request.image_base64:
            try:
                # Save base64 image to temp file
                image_data = base64.b64decode(request.image_base64)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_file.write(image_data)
                    temp_image_path = temp_file.name
                
                # Try vision analysis
                encoded_image = encode_image(temp_image_path)
                analysis = analyze_image_with_query(
                    query=full_query,
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    encoded_image=encoded_image
                )
                
                # Clean up temp file
                os.unlink(temp_image_path)
                
            except Exception as vision_error:
                print(f"Vision analysis failed: {vision_error}")
                # Fallback to text-only analysis
                analysis = await text_only_analysis(request.query, groq_api_key)
        else:
            # Text-only analysis
            analysis = await text_only_analysis(request.query, groq_api_key)
        
        return AnalysisResponse(
            analysis=analysis,
            success=True,
            message="Analysis completed successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def text_only_analysis(query: str, groq_api_key: str) -> str:
    """Fallback text-only medical analysis"""
    from groq import Groq
    
    client = Groq(api_key=groq_api_key)
    
    medical_prompt = f"""You are a medical AI assistant for educational purposes only.

Patient describes: "{query}"

Please provide:
1. A brief assessment based on the description
2. Possible causes or conditions to consider  
3. General care recommendations
4. When to seek immediate medical attention

Keep your response concise (2-3 sentences) and always recommend consulting a healthcare professional for proper diagnosis."""
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": medical_prompt}],
        max_tokens=200,
        temperature=0.7
    )
    
    return completion.choices[0].message.content

# Text-to-Speech endpoint
@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(request: SynthesisRequest):
    """Convert text to speech using ElevenLabs"""
    
    try:
        elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not configured")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"response_{timestamp}.mp3"
        output_path = f"static/audio/{output_filename}"
        
        # Create static directory if it doesn't exist
        os.makedirs("static/audio", exist_ok=True)
        
        # Generate speech
        try:
            audio_file = text_to_speech_with_elevenlabs(request.text, output_path)
            
            # Return URL to audio file
            audio_url = f"/audio/{output_filename}"
            
            return SynthesisResponse(
                audio_url=audio_url,
                success=True,
                message="Speech synthesized successfully"
            )
        except Exception as tts_error:
            # Fallback response when TTS fails
            return SynthesisResponse(
                audio_url="",
                success=False,
                message=f"Speech synthesis temporarily unavailable: {str(tts_error)}"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

# Complete consultation endpoint
@app.post("/consultation", response_model=ConsultationResponse)
async def full_consultation(
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    query: Optional[str] = Form(None)
):
    """Complete AI doctor consultation workflow"""
    
    transcription = None
    analysis = ""
    audio_url = None
    
    try:
        # Step 1: Transcribe audio if provided
        if audio:
            transcribe_response = await transcribe_audio(audio)
            if transcribe_response.success:
                transcription = transcribe_response.transcription
                query = transcription
        
        if not query:
            raise HTTPException(status_code=400, detail="No query provided (audio or text)")
        
        # Step 2: Analyze query with optional image
        image_base64 = None
        if image:
            image_content = await image.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        analysis_request = AnalysisRequest(query=query, image_base64=image_base64)
        analysis_response = await analyze_medical_query(analysis_request)
        
        if analysis_response.success:
            analysis = analysis_response.analysis
        
        # Step 3: Generate voice response
        if analysis and not analysis.startswith("Error"):
            synthesis_request = SynthesisRequest(text=analysis)
            synthesis_response = await synthesize_speech(synthesis_request)
            if synthesis_response.success:
                audio_url = synthesis_response.audio_url
        
        return ConsultationResponse(
            transcription=transcription,
            analysis=analysis,
            audio_url=audio_url,
            success=True,
            message="Consultation completed successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consultation failed: {str(e)}")

# Serve audio files
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio files"""
    file_path = f"static/audio/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
