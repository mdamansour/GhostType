"""
Core controller - Orchestrates all components with producer-consumer pattern.
"""

import logging
import queue
import threading
import time

from src.config import Config
from src.services.audio import AudioCapture
from src.services.input_hook import InputHook
from src.core.engine import VoskEngine

logger = logging.getLogger(__name__)


class Controller:
    """
    Main controller coordinating audio capture, speech recognition, and output.
    Implements producer-consumer pattern with thread-safe queues.
    """
    
    def __init__(self):
        """Initialize controller with all components."""
        self.config = Config()
        
        # Queues for producer-consumer pattern
        self.audio_queue = queue.Queue(maxsize=1000)
        self.text_queue = queue.Queue(maxsize=100)
        
        # Components
        self.audio_service = None
        self.engine = None
        self.input_hook = None
        
        # Threading
        self.worker_thread = None
        self.stop_event = threading.Event()
        
        # State
        self.is_recording = False
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all service components."""
        try:
            # Audio capture
            self.audio_service = AudioCapture(
                audio_queue=self.audio_queue,
                sample_rate=self.config.get('audio.sample_rate', 16000),
                channels=self.config.get('audio.channels', 1),
                chunk_duration_ms=self.config.get('audio.chunk_duration_ms', 100)
            )
            
            # Speech engine
            model_path = self.config.get('speech.model_path', './models/vosk-model-small-en-us-0.15')
            self.engine = VoskEngine(
                model_path=model_path,
                sample_rate=self.config.get('audio.sample_rate', 16000)
            )
            
            # Input hook
            hotkey = self.config.get('hotkeys.ptt', 'ctrl+alt')
            self.input_hook = InputHook(
                hotkey=hotkey,
                on_press=self._on_hotkey_press,
                on_release=self._on_hotkey_release
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _on_hotkey_press(self):
        """Callback when PTT hotkey is pressed."""
        if not self.is_recording:
            logger.info("[Recording started]")
            self.is_recording = True
            self.audio_service.start()
    
    def _on_hotkey_release(self):
        """Callback when PTT hotkey is released."""
        if self.is_recording:
            logger.info("[Recording stopped]")
            self.is_recording = False
            self.audio_service.stop()
            
            # Get final result from engine
            final_text = self.engine.finalize()
            if final_text:
                self.text_queue.put(final_text)
    
    def _worker_loop(self):
        """
        Worker thread that processes audio chunks.
        Consumes from audio_queue, processes with engine, produces to text_queue.
        """
        logger.info("Worker thread started")
        
        while not self.stop_event.is_set():
            try:
                # Get audio chunk with timeout
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # Process with speech engine
                text = self.engine.process_audio(audio_chunk)
                
                # If we got text, put it in text queue
                if text:
                    self.text_queue.put(text)
                
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")
        
        logger.info("Worker thread stopped")
    
    def start(self):
        """Start the controller and all services."""
        logger.info("Starting GhostType controller...")
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        # Start input hook
        self.input_hook.start()
        
        logger.info("Controller started successfully")
        logger.info(f"Press {self.config.get('hotkeys.ptt')} to start dictating")
    
    def stop(self):
        """Stop the controller and cleanup."""
        logger.info("Stopping GhostType controller...")
        
        # Stop recording if active
        if self.is_recording:
            self.audio_service.stop()
        
        # Stop input hook
        if self.input_hook:
            self.input_hook.stop()
        
        # Signal worker thread to stop
        self.stop_event.set()
        
        # Wait for worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        logger.info("Controller stopped")
    
    def get_text(self, timeout: float = None) -> str:
        """
        Get transcribed text from queue.
        
        Args:
            timeout: Maximum time to wait for text
            
        Returns:
            Transcribed text or None if timeout
        """
        try:
            return self.text_queue.get(timeout=timeout)
        except queue.Empty:
            return None
