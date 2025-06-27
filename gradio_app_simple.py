# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
from groq import Groq

from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

# System prompt for the AI doctor
system_prompt = """You are a medical AI assistant for educational purposes only. Based on the patient's description, provide general medical information and suggest when to seek professional care. Always remind patients that this is not a substitute for professional medical advice."""

def transcribe_audio_simple(audio_filepath):
    """Simple transcription function"""
    if not audio_filepath:
        return "No audio provided"
    
    if not os.path.exists(audio_filepath):
        return f"Audio file not found: {audio_filepath}"
    
    try:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return "GROQ_API_KEY not found in environment variables"
        
        result = transcribe_with_groq(
            audio_filepath=audio_filepath,
            GROQ_API_KEY=groq_api_key,
            stt_model="whisper-large-v3"
        )
        return result
    except Exception as e:
        return f"Transcription error: {str(e)}"

def medical_analysis_text_only(query_text):
    """Text-only medical analysis that works reliably"""
    if not query_text or query_text.startswith("Error") or query_text.startswith("No"):
        return "Please provide a description of your symptoms for analysis."
    
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        medical_prompt = f"""{system_prompt}

Patient describes: "{query_text}"

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
        
    except Exception as e:
        return f"I'm unable to provide analysis at the moment. For your symptoms '{query_text}', please consult with a medical professional for proper evaluation and treatment."

def generate_voice_simple(text):
    """Simple voice generation function"""
    if not text or text.startswith("Error") or text.startswith("No") or text.startswith("Please"):
        return None
    
    try:
        output_file = "doctor_response.mp3"
        result = text_to_speech_with_elevenlabs(text, output_file)
        return result
    except Exception as e:
        print(f"Voice generation error: {str(e)}")
        return None

def process_medical_consultation(audio_file, image_file, progress=gr.Progress()):
    """Process medical consultation with text-only analysis"""
    
    transcription = ""
    medical_response = ""
    audio_output = None
    
    try:
        # Step 1: Transcribe audio
        progress(0.3, desc="Transcribing your description...")
        if audio_file:
            transcription = transcribe_audio_simple(audio_file)
            if transcription.startswith("Error") or transcription.startswith("No"):
                return transcription, "Could not process audio", None
        else:
            return "No audio provided", "Please record your symptoms first", None
        
        # Step 2: Medical analysis (text-only for reliability)
        progress(0.6, desc="Analyzing symptoms...")
        medical_response = medical_analysis_text_only(transcription)
        
        # Add image note if provided
        if image_file:
            medical_response += "\n\nNote: I cannot currently analyze images, but based on your description above, please consult a healthcare provider who can examine the visual symptoms directly."
        
        # Step 3: Generate voice response
        progress(0.9, desc="Generating voice response...")
        audio_output = generate_voice_simple(medical_response)
        
        progress(1.0, desc="Complete!")
        return transcription, medical_response, audio_output
        
    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        return transcription or "Error during transcription", error_msg, None

# Create the Gradio interface
with gr.Blocks(
    title="AI Medical Assistant", 
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    """
) as demo:
    
    gr.Markdown(
        """
        # 🩺 AI Medical Assistant - Voice & Text
        
        **How it works:**
        1. 🎤 Record your symptoms description
        2. 📸 Optionally upload an image (for context)
        3. 🔍 Get medical guidance and recommendations
        
        ⚠️ **Important**: This is for educational purposes only. Always consult a real healthcare professional for medical advice.
        """
    )
    
    with gr.Row():
        # Input Column
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Describe Your Symptoms")
            
            audio_input = gr.Audio(
                label="🎤 Record Your Symptoms",
                sources=["microphone"],
                type="filepath",
                format="wav",
                show_download_button=False,
                interactive=True
            )
            
            image_input = gr.Image(
                label="📸 Upload Image (Optional)", 
                type="filepath",
                height=250
            )
            
            analyze_btn = gr.Button(
                "🔍 Get Medical Guidance", 
                variant="primary", 
                size="lg"
            )
        
        # Output Column  
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Medical Guidance")
            
            transcription_output = gr.Textbox(
                label="🗣️ Your Description",
                interactive=False,
                max_lines=3
            )
            
            medical_output = gr.Textbox(
                label="👨‍⚕️ Medical Guidance", 
                interactive=False,
                max_lines=10
            )
            
            audio_output = gr.Audio(
                label="🔊 Voice Response",
                interactive=False,
                autoplay=True
            )
    
    # Connect the button to the processing function
    analyze_btn.click(
        fn=process_medical_consultation,
        inputs=[audio_input, image_input],
        outputs=[transcription_output, medical_output, audio_output],
        show_progress=True
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        debug=True,
        share=True,
        server_name="0.0.0.0",
        server_port=7862,
        show_error=True
    )
