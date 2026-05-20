import os
import logging
from typing import List, Tuple, Optional
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import with error handling
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    logger.error("Whisper not available. Install with: pip install openai-whisper")
    WHISPER_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.error("Transformers not available. Install with: pip install transformers torch")
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
    logger.error("spaCy not available. Install with: pip install spacy")
    SPACY_AVAILABLE = False

try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    logger.error("BERTopic not available. Install with: pip install bertopic")
    BERTOPIC_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    logger.error("XGBoost not available. Install with: pip install xgboost")
    XGBOOST_AVAILABLE = False

# Initialize models safely
def transcribe_audio(audio_path: str) -> Optional[str]:
    """Transcribe audio using Whisper."""
    if not WHISPER_AVAILABLE:
        logger.error("Whisper not available")
        return None
    
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return None

# Initialize transformers components safely
tokenizer = None
embed_model = None
if TRANSFORMERS_AVAILABLE:
    try:
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        embed_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        logger.error(f"Error loading transformer models: {e}")

def embed_text(text: str) -> Optional[List[float]]:
    """Generate text embeddings."""
    if not TRANSFORMERS_AVAILABLE or not tokenizer or not embed_model:
        logger.error("Transformers not available")
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
        logger.error("spaCy not available")
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
        topic_model = BERTopic(verbose=True)
    except Exception as e:
        logger.error(f"Error initializing BERTopic: {e}")

def fit_bertopic(docs: List[str]) -> Tuple[List[int], List[float]]:
    """Fit BERTopic model to documents."""
    if not BERTOPIC_AVAILABLE or not topic_model:
        logger.error("BERTopic not available")
        return [], []
    
    try:
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

# Fix XGBoost model
class DummyXGBModel:
    """Dummy model for demonstration purposes."""
    def predict(self, X) -> List[int]:
        # Return safe index values
        return [1]  # 1 = Intermediate

    def predict_proba(self, X):
        # Return dummy probabilities
        return [[0.1, 0.8, 0.1]]  # Beginner, Intermediate, Advanced

difficulty_model = DummyXGBModel()

import numpy as np
import re

def extract_features(text: str) -> Optional[np.ndarray]:
    """Extract features from text for difficulty prediction."""
    try:
        words = text.split()
        avg_word_len = np.mean([len(w) for w in words]) if words else 0
        sent_count = text.count('.') + text.count('!') + text.count('?')
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

# FastAPI components
try:
    from fastapi import FastAPI, UploadFile, File, HTTPException
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.error("FastAPI not available. Install with: pip install fastapi uvicorn python-multipart")
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    app = FastAPI(title="Educational Video Tagging API")
    
    @app.post("/analyze/")
    async def analyze_upload(file: UploadFile = File(...)):
        """Analyze uploaded audio file."""
        if not WHISPER_AVAILABLE:
            raise HTTPException(status_code=503, detail="Whisper not available")
        
        temp_dir = tempfile.mkdtemp()
        try:
            audio_path = os.path.join(temp_dir, f"temp_{file.filename}")
            
            with open(audio_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            transcript = transcribe_audio(audio_path)
            if transcript is None:
                raise HTTPException(status_code=500, detail="Failed to transcribe audio")
            
            entities = extract_entities(transcript)
            embedding = embed_text(transcript)
            
            topics, probs = [], []
            if BERTOPIC_AVAILABLE and topic_model:
                topics, probs = fit_bertopic([transcript])
            
            difficulty = predict_difficulty(transcript)
            
            topic_keywords = []
            if topics and len(topics) > 0:
                topic_keywords = get_topic_keywords(topics[0]) if topics[0] >= 0 else []
            
            return {
                "transcript": transcript,
                "entities": entities,
                "topic_keywords": [kw[0] for kw in topic_keywords],
                "difficulty": difficulty
            }
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

# Streamlit components
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        if FASTAPI_AVAILABLE:
            uvicorn.run(app, host="0.0.0.0", port=8000)
        else:
            logger.error("Cannot start API - FastAPI not available")
    else:
        try:
            import streamlit as st
            import requests
            
            st.title("Educational Video Tagging Prototype")
            
            uploaded_file = st.file_uploader("Upload audio file (mp3/wav)", type=["mp3", "wav"])
            
            if uploaded_file:
                if st.button("Analyze"):
                    with st.spinner("Processing audio and analyzing..."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                            response = requests.post("http://localhost:8000/analyze/", files=files)
                            
                            if response.status_code == 200:
                                data = response.json()
                                st.subheader("Transcript")
                                st.write(data["transcript"])
                                
                                st.subheader("Named Entities")
                                for ent, label in data["entities"]:
                                    st.write(f"{ent} — {label}")
                                
                                st.subheader("Topic Keywords")
                                for word in data["topic_keywords"]:
                                    st.write(word)
                                
                                st.subheader("Estimated Difficulty Level")
                                st.write(data["difficulty"])
                            else:
                                st.error(f"API error: {response.status_code} - {response.text}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API. Please start the API server with: python test.py api")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.info("Upload an audio file to start analysis.")
                
        except ImportError:
            logger.error("Streamlit not available. Install with: pip install streamlit requests")
            logger.info("To run API: python test.py api")
            logger.info("To run Streamlit: streamlit run test.py")
