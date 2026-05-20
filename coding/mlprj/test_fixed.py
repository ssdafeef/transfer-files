import os
import logging
from typing import List, Tuple, Optional
import tempfile
import shutil
import io
import wave
import numpy as np

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enhanced error handling for imports
def check_dependencies():
    """Check and report on all required dependencies."""
    missing_deps = []
    
    try:
        import whisper
        logger.info("✅ Whisper available")
    except ImportError:
        missing_deps.append("openai-whisper")
        logger.error("❌ Whisper not available")

    try:
        import torch
        logger.info(f"✅ PyTorch available (version: {torch.__version__})")
    except ImportError:
        missing_deps.append("torch")
        logger.error("❌ PyTorch not available")

    try:
        from transformers import AutoTokenizer, AutoModel
        logger.info("✅ Transformers available")
    except ImportError:
        missing_deps.append("transformers")
        logger.error("❌ Transformers not available")

    try:
        import spacy
        logger.info("✅ spaCy available")
    except ImportError:
        missing_deps.append("spacy")
        logger.error("❌ spaCy not available")

    try:
        import fastapi
        logger.info("✅ FastAPI available")
    except ImportError:
        missing_deps.append("fastapi")
        logger.error("❌ FastAPI not available")

    try:
        import uvicorn
        logger.info("✅ Uvicorn available")
    except ImportError:
        missing_deps.append("uvicorn")
        logger.error("❌ Uvicorn not available")

    if missing_deps:
        logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.error("Install with: pip install " + " ".join(missing_deps))
        return False
    
    return True

# Import with enhanced error handling
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.error("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False

try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

# Audio validation and preprocessing
def validate_audio_file(file_path: str) -> bool:
    """Validate audio file format and properties."""
    try:
        # Check file exists and has content
        if not os.path.exists(file_path):
            logger.error(f"Audio file does not exist: {file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.error("Audio file is empty")
            return False
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            logger.error("Audio file too large (>50MB)")
            return False
        
        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in valid_extensions:
            logger.error(f"Unsupported audio format: {file_ext}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating audio file: {e}")
        return False

def convert_audio_to_wav(input_path: str, output_path: str) -> bool:
    """Convert audio to WAV format using available tools."""
    try:
        # Try using pydub first
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_path, format="wav")
            return True
        except ImportError:
            logger.warning("pydub not available, trying native WAV")
        
        # Fallback: try to read as WAV directly
        if input_path.lower().endswith('.wav'):
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        logger.error("No audio conversion tools available")
        return False
        
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        return False

# Enhanced audio transcription with better error handling
def transcribe_audio(audio_path: str) -> Optional[str]:
    """Transcribe audio using Whisper with enhanced error handling."""
    if not WHISPER_AVAILABLE:
        logger.error("Whisper not available for transcription")
        return None
    
    if not validate_audio_file(audio_path):
        return None
    
    try:
        logger.info(f"Starting transcription of: {audio_path}")
        
        # Ensure audio is in correct format
        temp_wav = None
        if not audio_path.lower().endswith('.wav'):
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav.close()
            
            if not convert_audio_to_wav(audio_path, temp_wav.name):
                logger.error("Failed to convert audio to WAV format")
                return None
            
            audio_path = temp_wav.name
        
        # Load Whisper model with error handling
        try:
            model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return None
        
        # Perform transcription with detailed logging
        try:
            result = model.transcribe(
                audio_path,
                language="en",
                task="transcribe",
                verbose=False
            )
            
            transcript = result.get("text", "").strip()
            if not transcript:
                logger.warning("Transcription produced empty text")
                return None
            
            logger.info(f"Transcription successful: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Unexpected error during transcription: {e}")
        return None
    
    finally:
        # Clean up temporary file
        if temp_wav and os.path.exists(temp_wav.name):
            try:
                os.unlink(temp_wav.name)
            except:
                pass

# Initialize transformers components safely
tokenizer = None
embed_model = None
if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
    try:
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        embed_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Transformers models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading transformer models: {e}")

def embed_text(text: str) -> Optional[List[float]]:
    """Generate text embeddings with error handling."""
    if not TRANSFORMERS_AVAILABLE or not TORCH_AVAILABLE or not tokenizer or not embed_model:
        logger.error("Transformers not available for embeddings")
        return None
    
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            embeddings = embed_model(**inputs).last_hidden_state[:, 0, :]
        return embeddings.squeeze().numpy().tolist()
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return None

def extract_entities(text: str) -> List[Tuple[str, str]]:
    """Extract named entities from text."""
    if not SPACY_AVAILABLE or not nlp:
        logger.error("spaCy not available for entity extraction")
        return []
    
    try:
        doc = nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return []

# Initialize BERTopic safely
topic_model = None
if BERTOPIC_AVAILABLE:
    try:
        topic_model = BERTopic(verbose=False)  # Reduce verbosity
        logger.info("BERTopic initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing BERTopic: {e}")

def fit_bertopic(docs: List[str]) -> Tuple[List[int], List[float]]:
    """Fit BERTopic model to documents."""
    if not BERTOPIC_AVAILABLE or not topic_model:
        logger.error("BERTopic not available")
        return [], []
    
    try:
        if len(docs) < 2:
            logger.warning("Need at least 2 documents for BERTopic")
            return [], []
        
        topics, probs = topic_model.fit_transform(docs)
        return topics, probs
    except Exception as e:
        logger.error(f"Error fitting BERTopic: {e}")
        return [], []

def get_topic_keywords(topic_id: int, top_n: int = 10) -> List[Tuple[str, float]]:
    """Get topic keywords from BERTopic."""
    if not BERTOPIC_AVAILABLE or not topic_model:
        logger.error("BERTopic not available")
        return []
    
    try:
        topic_info = topic_model.get_topic(topic_id)
        return topic_info[:top_n] if topic_info else []
    except Exception as e:
        logger.error(f"Error getting topic keywords: {e}")
        return []

# Enhanced difficulty prediction
class DummyXGBModel:
    """Dummy model for demonstration purposes."""
    def predict(self, X) -> List[int]:
        return [1]  # 1 = Intermediate

    def predict_proba(self, X):
        return [[0.1, 0.8, 0.1]]  # Beginner, Intermediate, Advanced

difficulty_model = DummyXGBModel()

def extract_features(text: str) -> Optional[np.ndarray]:
    """Extract features from text for difficulty prediction."""
    try:
        words = text.split()
        avg_word_len = np.mean([len(w) for w in words]) if words else 0
        sent_count = max(text.count('.') + text.count('!') + text.count('?'), 1)
        word_count = len(words)
        complex_word_ratio = len([w for w in words if len(w) > 7]) / max(word_count, 1)
        return np.array([avg_word_len, sent_count, word_count, complex_word_ratio]).reshape(1, -1)
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        return None

def predict_difficulty(text: str) -> str:
    """Predict difficulty level of text."""
    try:
        features = extract_features(text)
        if features is None:
            return "Unknown"
        
        pred = difficulty_model.predict(features)
        levels = ["Beginner", "Intermediate", "Advanced"]
        idx = max(0, min(pred[0], len(levels) - 1))
        return levels[idx]
    except Exception as e:
        logger.error(f"Error predicting difficulty: {e}")
        return "Unknown"

# FastAPI components with enhanced error handling
try:
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.error("FastAPI not available. Install with: pip install fastapi uvicorn python-multipart")
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Educational Video Tagging API",
        description="Enhanced API with better error handling and audio processing"
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "whisper_available": WHISPER_AVAILABLE,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "spacy_available": SPACY_AVAILABLE,
            "bertopic_available": BERTOPIC_AVAILABLE
        }
    
    @app.post("/analyze/")
    async def analyze_upload(file: UploadFile = File(...)):
        """Analyze uploaded audio file with enhanced error handling."""
        if not WHISPER_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Whisper not available. Please install: pip install openai-whisper"
            )
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.content_type}. Please upload an audio file."
            )
        
        temp_dir = tempfile.mkdtemp()
        try:
            audio_path = os.path.join(temp_dir, f"temp_{file.filename}")
            
            # Save uploaded file
            try:
                content = await file.read()
                if len(content) == 0:
                    raise HTTPException(status_code=400, detail="Empty file uploaded")
                
                with open(audio_path, "wb") as f:
                    f.write(content)
                
                logger.info(f"Received file: {file.filename} ({len(content)} bytes)")
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error saving uploaded file: {str(e)}")
            
            # Validate audio file
            if not validate_audio_file(audio_path):
                raise HTTPException(status_code=400, detail="Invalid audio file format or content")
            
            # Transcribe audio
            transcript = transcribe_audio(audio_path)
            if transcript is None:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to transcribe audio. Please check the audio file format and content."
                )
            
            # Extract additional information
            entities = extract_entities(transcript)
            embedding = embed_text(transcript)
            
            topics, probs = [], []
            if BERTOPIC_AVAILABLE and topic_model and len([transcript]) >= 1:
                try:
                    topics, probs = fit_bertopic([transcript])
                except Exception as e:
                    logger.warning(f"BERTopic analysis failed: {e}")
            
            difficulty = predict_difficulty(transcript)
            
            topic_keywords = []
            if topics and len(topics) > 0 and topics[0] >= 0:
                topic_keywords = get_topic_keywords(topics[0])
            
            return {
                "transcript": transcript,
                "entities": entities,
                "topic_keywords": [kw[0] for kw in topic_keywords],
                "difficulty": difficulty,
                "audio_duration": len(transcript.split()) / 150  # Rough estimate
            }
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Unexpected error in analyze_upload: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

# Main execution
if __name__ == "__main__":
    import sys
    
    # Check dependencies on startup
    if not check_dependencies():
        logger.error("Missing required dependencies. Please install them and try again.")
        sys.exit(1)
    
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        if FASTAPI_AVAILABLE:
            logger.info("Starting API server...")
            uvicorn.run(app, host="0.0.0.0", port=8000)
        else:
            logger.error("Cannot start API - FastAPI not available")
    else:
        try:
            import streamlit as st
            import requests
            
            st.title("Educational Video Tagging Prototype")
            st.write("Enhanced version with better error handling")
            
            # Check API health
            try:
                health_response = requests.get("http://localhost:8000/health", timeout=2)
                if health_response.status_code == 200:
                    st.success("✅ API is running")
                else:
                    st.warning("⚠️ API may have issues")
            except:
                st.error("❌ API not running. Start with: python test_fixed.py api")
            
            uploaded_file = st.file_uploader(
                "Upload audio file (mp3/wav/m4a/flac/ogg)", 
                type=["mp3", "wav", "m4a", "flac", "ogg"]
            )
            
            if uploaded_file:
                if st.button("Analyze"):
                    with st.spinner("Processing audio and analyzing..."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                            response = requests.post("http://localhost:8000/analyze/", files=files)
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                st.subheader("📄 Transcript")
                                st.write(data["transcript"])
                                
                                st.subheader("🏷️ Named Entities")
                                if data["entities"]:
                                    for ent, label in data["entities"]:
                                        st.write(f"**{ent}** — {label}")
                                else:
                                    st.write("No entities found")
                                
                                st.subheader("🔑 Topic Keywords")
                                if data["topic_keywords"]:
                                    for word in data["topic_keywords"]:
                                        st.write(f"• {word}")
                                else:
                                    st.write("No topic keywords extracted")
                                
                                st.subheader("📊 Estimated Difficulty Level")
                                st.info(f"**{data['difficulty']}**")
                                
                                st.subheader("⏱️ Estimated Duration")
                                st.write(f"~{data['audio_duration']:.1f} minutes")
                                
                            else:
                                error_detail = response.json().get('detail', 'Unknown error')
                                st.error(f"API error: {response.status_code} - {error_detail}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API. Please start the API server with: python test_fixed.py api")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.info("Upload an audio file to start analysis.")
                
        except ImportError:
            logger.error("Streamlit not available. Install with: pip install streamlit requests")
            logger.info("To run API: python test_fixed.py api")
            logger.info("To run Streamlit: streamlit run test_fixed.py")
