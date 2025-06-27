# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import asyncio
from concurrent.futures import ThreadPoolExecutor

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

# System prompt for the AI doctor
system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

def transcribe_audio_simple(audio_filepath):
    """Simple transcription function with better error handling"""
    if not audio_filepath:
        return "No audio provided"
    
    if not os.path.exists(audio_filepath):
        return f"Audio file not found: {audio_filepath}"
    
    try:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return "GROQ_API_KEY not found in environment variables"
        
        # Call the transcription function with correct parameters
        result = transcribe_with_groq(
            audio_filepath=audio_filepath,
            GROQ_API_KEY=groq_api_key,
            stt_model="whisper-large-v3"
        )
        return result
    except Exception as e:
        return f"Transcription error: {str(e)}"

def analyze_image_simple(image_filepath, query_text):
    """Simple image analysis function with fallback"""
    if not image_filepath:
        return "No image provided for analysis"
    
    try:
        # First try with vision model
        full_query = system_prompt + " " + query_text
        encoded_image = encode_image(image_filepath)
        result = analyze_image_with_query(
            query=full_query,
            encoded_image=encoded_image,
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
        return result
    except Exception as vision_error:
        print(f"Vision model failed: {vision_error}")
        
        # Fallback to text-only analysis
        try:
            from groq import Groq
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            fallback_prompt = f"""Based on the patient's description: '{query_text}', provide a medical assessment. 
            Act as a professional doctor (for educational purposes). Provide a concise medical opinion and suggest remedies.
            Keep your response to 2-3 sentences maximum. Start with 'Based on your description...'"""
            
            print(f"Using fallback text-only analysis...")
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": fallback_prompt}],
                max_tokens=150
            )
            
            return completion.choices[0].message.content
            
        except Exception as fallback_error:
            print(f"Fallback also failed: {fallback_error}")
            return f"I apologize, but I'm unable to analyze images at the moment. Based on your description '{query_text}', I recommend consulting with a medical professional for proper diagnosis and treatment."

def generate_voice_simple(text):
    """Simple voice generation function"""
    if not text or text.startswith("Error") or text.startswith("No"):
        return None
    
    try:
        output_file = "doctor_response.mp3"
        result = text_to_speech_with_elevenlabs(text, output_file)
        return result
    except Exception as e:
        print(f"Voice generation error: {str(e)}")
        return None

def process_inputs_optimized(audio_file, image_file, progress=gr.Progress()):
    """Optimized processing function with progress tracking"""
    
    # Initialize results
    transcription = ""
    doctor_response = ""
    audio_output = None
    
    try:
        # Step 1: Transcribe audio
        progress(0.2, desc="Transcribing audio...")
        if audio_file:
            transcription = transcribe_audio_simple(audio_file)
            if transcription.startswith("Error") or transcription.startswith("No"):
                return transcription, "Could not process audio", None
        else:
            transcription = "No audio provided"
            return transcription, "Please record some audio first", None
        
        # Step 2: Analyze image with transcribed text
        progress(0.5, desc="Analyzing image...")
        if image_file:
            doctor_response = analyze_image_simple(image_file, transcription)
        else:
            doctor_response = f"Based on your description: '{transcription}', I would need to see an image to provide a proper medical assessment. Please upload an image of the area you're concerned about."
        
        # Step 3: Generate voice response
        progress(0.8, desc="Generating voice response...")
        if not doctor_response.startswith("Error"):
            audio_output = generate_voice_simple(doctor_response)
        
        progress(1.0, desc="Complete!")
        return transcription, doctor_response, audio_output
        
    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        return transcription or "Error during transcription", error_msg, None

# Create the Gradio interface
with gr.Blocks(
    title="AI Doctor - Voice & Vision", 
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    """
) as demo:
    
    gr.Markdown(
        """
        # 🩺 AI Doctor with Voice & Vision
        
        **Instructions:**
        1. 🎤 Record your voice describing your symptoms
        2. 📸 Upload a clear image of the medical concern
        3. 🔍 Click "Analyze" to get your AI doctor's assessment
        """
    )
    
    with gr.Row():
        # Input Column
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Your Input")
            
            audio_input = gr.Audio(
                label="🎤 Record Your Symptoms",
                sources=["microphone"],
                type="filepath",
                format="wav",
                show_download_button=False,
                interactive=True
            )
            
            image_input = gr.Image(
                label="📸 Upload Medical Image", 
                type="filepath",
                height=300
            )
            
            analyze_btn = gr.Button(
                "🔍 Analyze", 
                variant="primary", 
                size="lg",
                scale=1
            )
            
            gr.Markdown("*Note: This is for educational purposes only. Always consult a real doctor for medical advice.*")
        
        # Output Column  
        with gr.Column(scale=1):
            gr.Markdown("### 📤 AI Doctor's Response")
            
            transcription_output = gr.Textbox(
                label="🗣️ What You Said",
                interactive=False,
                max_lines=3
            )
            
            diagnosis_output = gr.Textbox(
                label="👨‍⚕️ Doctor's Assessment", 
                interactive=False,
                max_lines=8
            )
            
            audio_output = gr.Audio(
                label="🔊 Doctor's Voice Response",
                interactive=False,
                autoplay=True
            )
    
    # Connect the button to the processing function
    analyze_btn.click(
        fn=process_inputs_optimized,
        inputs=[audio_input, image_input],
        outputs=[transcription_output, diagnosis_output, audio_output],
        show_progress=True
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        debug=True,
        share=True,
        server_name="0.0.0.0",
        server_port=7861,
        show_error=True
    )
