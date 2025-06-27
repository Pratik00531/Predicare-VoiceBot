/**
 * TypeScript API Client for Predicare VoiceBot
 * Use this in your TypeScript frontend to interact with the AI Doctor API
 */

// API Response Types
export interface TranscriptionResponse {
  transcription: string;
  success: boolean;
  message: string;
}

export interface AnalysisResponse {
  analysis: string;
  success: boolean;
  message: string;
}

export interface SynthesisResponse {
  audio_url: string;
  success: boolean;
  message: string;
}

export interface ConsultationResponse {
  transcription?: string;
  analysis: string;
  audio_url?: string;
  success: boolean;
  message: string;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  services: {
    groq: boolean;
    elevenlabs: boolean;
  };
}

// API Client Class
export class PredicareAPI {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await fetch(`${this.baseURL}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  // Transcribe audio to text
  async transcribeAudio(audioFile: File): Promise<TranscriptionResponse> {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch(`${this.baseURL}/transcribe`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Transcription failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Analyze medical query
  async analyzeMedicalQuery(
    query: string,
    imageBase64?: string
  ): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseURL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        image_base64: imageBase64,
      }),
    });

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Convert text to speech
  async synthesizeSpeech(text: string): Promise<SynthesisResponse> {
    const response = await fetch(`${this.baseURL}/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Speech synthesis failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Complete consultation workflow
  async fullConsultation(
    audioFile?: File,
    imageFile?: File,
    query?: string
  ): Promise<ConsultationResponse> {
    const formData = new FormData();
    
    if (audioFile) {
      formData.append('audio', audioFile);
    }
    
    if (imageFile) {
      formData.append('image', imageFile);
    }
    
    if (query) {
      formData.append('query', query);
    }

    const response = await fetch(`${this.baseURL}/consultation`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Consultation failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Get audio file URL
  getAudioURL(filename: string): string {
    return `${this.baseURL}/audio/${filename}`;
  }

  // Helper: Convert file to base64
  async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  }
}

// React Hook Example (if using React)
export const usePredicareAPI = () => {
  const api = new PredicareAPI();

  const transcribeAudio = async (audioFile: File) => {
    try {
      const result = await api.transcribeAudio(audioFile);
      return result;
    } catch (error) {
      console.error('Transcription error:', error);
      throw error;
    }
  };

  const analyzeMedical = async (query: string, imageFile?: File) => {
    try {
      let imageBase64: string | undefined;
      if (imageFile) {
        imageBase64 = await api.fileToBase64(imageFile);
      }
      
      const result = await api.analyzeMedicalQuery(query, imageBase64);
      return result;
    } catch (error) {
      console.error('Analysis error:', error);
      throw error;
    }
  };

  const synthesizeSpeech = async (text: string) => {
    try {
      const result = await api.synthesizeSpeech(text);
      return result;
    } catch (error) {
      console.error('Speech synthesis error:', error);
      throw error;
    }
  };

  const fullConsultation = async (
    audioFile?: File,
    imageFile?: File,
    query?: string
  ) => {
    try {
      const result = await api.fullConsultation(audioFile, imageFile, query);
      return result;
    } catch (error) {
      console.error('Consultation error:', error);
      throw error;
    }
  };

  return {
    transcribeAudio,
    analyzeMedical,
    synthesizeSpeech,
    fullConsultation,
    api
  };
};

// Usage Examples:

/*
// Basic usage:
const api = new PredicareAPI('http://localhost:8000');

// Transcribe audio
const audioFile = document.getElementById('audio-input').files[0];
const transcription = await api.transcribeAudio(audioFile);
console.log(transcription.transcription);

// Analyze with image
const imageFile = document.getElementById('image-input').files[0];
const imageBase64 = await api.fileToBase64(imageFile);
const analysis = await api.analyzeMedicalQuery("I have a rash", imageBase64);
console.log(analysis.analysis);

// Full consultation
const consultation = await api.fullConsultation(audioFile, imageFile);
console.log(consultation);

// React Component Example:
function MedicalConsultation() {
  const { fullConsultation } = usePredicareAPI();
  const [result, setResult] = useState(null);
  
  const handleConsultation = async (audioFile, imageFile) => {
    try {
      const consultation = await fullConsultation(audioFile, imageFile);
      setResult(consultation);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  return (
    <div>
      <input type="file" accept="audio/*" onChange={(e) => setAudioFile(e.target.files[0])} />
      <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />
      <button onClick={() => handleConsultation(audioFile, imageFile)}>
        Start Consultation
      </button>
      {result && (
        <div>
          <p>Transcription: {result.transcription}</p>
          <p>Analysis: {result.analysis}</p>
          {result.audio_url && <audio src={result.audio_url} controls />}
        </div>
      )}
    </div>
  );
}
*/
