"""
Vosk speech recognition engine wrapper.
"""

import json
import logging
import os
import sys
from pathlib import Path
from vosk import Model, KaldiRecognizer

logger = logging.getLogger(__name__)


class VoskEngine:
    """
    Wrapper for Vosk speech recognition engine.
    """
    
    def __init__(self, model_path: str, sample_rate: int = 16000):
        """
        Initialize Vosk engine.
        
        Args:
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate in Hz
        """
        self.model_path = self._resolve_model_path(model_path)
        self.sample_rate = sample_rate
        self.model = None
        self.recognizer = None
        
        self._load_model()
    
    def _resolve_model_path(self, model_path: str) -> Path:
        """
        Resolve model path, handling PyInstaller bundled resources.
        
        Args:
            model_path: Original model path from config
            
        Returns:
            Resolved Path object
        """
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = Path(sys._MEIPASS)
        else:
            # Running from source
            base_path = Path(__file__).parent.parent.parent
        
        # Try relative to base path
        full_path = base_path / model_path
        if full_path.exists():
            return full_path
        
        # Try as absolute path
        full_path = Path(model_path)
        if full_path.exists():
            return full_path
        
        # Model not found
        logger.error(f"Vosk model not found at: {model_path}")
        logger.error(f"Searched in: {base_path / model_path} and {model_path}")
        raise FileNotFoundError(f"Vosk model not found: {model_path}")
    
    def _load_model(self):
        """Load Vosk model from disk."""
        try:
            logger.info(f"Loading Vosk model from: {self.model_path}")
            
            # Validate model files exist
            required_files = ['am/final.mdl', 'graph/HCLR.fst', 'conf/model.conf']
            for file in required_files:
                file_path = self.model_path / file
                if not file_path.exists():
                    raise FileNotFoundError(f"Missing model file: {file}")
            
            # Load model
            self.model = Model(str(self.model_path))
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            
            logger.info("Vosk model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise
    
    def process_audio(self, audio_bytes: bytes) -> str:
        """
        Process audio chunk and return transcribed text.
        
        Args:
            audio_bytes: Raw audio data as bytes
            
        Returns:
            Transcribed text string, or empty string if no final result yet
        """
        if self.recognizer is None:
            logger.error("Recognizer not initialized")
            return ""
        
        try:
            # Feed audio to recognizer
            if self.recognizer.AcceptWaveform(audio_bytes):
                # Final result available
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '')
                if text:
                    logger.debug(f"Transcribed: {text}")
                return text
            else:
                # Partial result (not used in Phase 1)
                return ""
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return ""
    
    def finalize(self) -> str:
        """
        Get final result after stopping audio input.
        
        Returns:
            Final transcribed text
        """
        if self.recognizer is None:
            return ""
        
        try:
            result = json.loads(self.recognizer.FinalResult())
            text = result.get('text', '')
            
            # Reset recognizer for next session
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            
            return text
            
        except Exception as e:
            logger.error(f"Error finalizing: {e}")
            return ""
