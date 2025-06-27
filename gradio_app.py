# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#VoiceBot UI with Gradio
import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

#load_dotenv()

system_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def process_inputs(audio_filepath, image_filepath):
    # Check if GROQ_API_KEY is available
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        return "Error: GROQ_API_KEY not found in environment variables", "Please set your GROQ_API_KEY in the .env file", None
    
    # Check if audio file exists
    if not audio_filepath:
        return "No audio provided", "Please record some audio first", None
    
    print(f"Audio file path: {audio_filepath}")
    print(f"Audio file exists: {os.path.exists(audio_filepath) if audio_filepath else 'No path'}")
    
    try:
        speech_to_text_output = transcribe_with_groq(GROQ_API_KEY=groq_api_key, 
                                                     audio_filepath=audio_filepath,
                                                     stt_model="whisper-large-v3")
        print(f"Speech to text output: {speech_to_text_output}")
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return f"Error in speech transcription: {str(e)}", "Speech to text failed", None

    # Handle the image input
    if image_filepath:
        try:
            doctor_response = analyze_image_with_query(query=system_prompt+speech_to_text_output, encoded_image=encode_image(image_filepath), model="meta-llama/llama-4-scout-17b-16e-instruct") #model="meta-llama/llama-4-maverick-17b-128e-instruct") 
        except Exception as e:
            doctor_response = f"Error analyzing image: {str(e)}"
    else:
        doctor_response = "No image provided for me to analyze"

    try:
        voice_of_doctor = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath="final.mp3") 
    except Exception as e:
        voice_of_doctor = None
        print(f"Error generating voice: {str(e)}")

    return speech_to_text_output, doctor_response, voice_of_doctor


# Create the interface with better configuration
with gr.Blocks(title="AI Doctor with Vision and Voice") as iface:
    gr.Markdown("# AI Doctor with Vision and Voice")
    gr.Markdown("Record your voice describing symptoms and upload a medical image for analysis")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                sources=["microphone"], 
                type="filepath", 
                label="Record your voice",
                format="wav"
            )
            image_input = gr.Image(type="filepath", label="Upload medical image")
            submit_btn = gr.Button("Analyze", variant="primary")
        
        with gr.Column():
            speech_output = gr.Textbox(label="Speech to Text", interactive=False)
            doctor_response = gr.Textbox(label="Doctor's Response", interactive=False)
            audio_output = gr.Audio(label="Doctor's Voice")
    
    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[speech_output, doctor_response, audio_output]
    )

iface.launch(debug=True, share=True)

#http://127.0.0.1:7860