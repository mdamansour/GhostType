"""
Audio capture service using sounddevice.
"""

import logging
import queue
import sounddevice as sd
import numpy as np

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Captures audio from microphone and pushes to queue.
    """
    
    def __init__(self, audio_queue: queue.Queue, sample_rate: int = 16000, 
                 channels: int = 1, chunk_duration_ms: int = 100):
        """
        Initialize audio capture service.
        
        Args:
            audio_queue: Queue to push audio chunks to
            sample_rate: Sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            chunk_duration_ms: Duration of each audio chunk in milliseconds
        """
        self.audio_queue = audio_queue
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration_ms = chunk_duration_ms
        self.blocksize = int(sample_rate * chunk_duration_ms / 1000)
        self.stream = None
        self.is_recording = False
        
        logger.info(f"AudioCapture initialized: {sample_rate}Hz, {channels}ch, {chunk_duration_ms}ms chunks")
    
    def _audio_callback(self, indata, frames, time, status):
        """
        Callback function called by sounddevice for each audio chunk.
        
        Args:
            indata: Audio data as numpy array
            frames: Number of frames
            time: Timing information
            status: Stream status
        """
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        if self.is_recording:
            # Convert to bytes and put in queue
            audio_bytes = bytes(indata)
            try:
                self.audio_queue.put(audio_bytes, block=False)
            except queue.Full:
                logger.warning("Audio queue full, dropping chunk")
    
    def start(self):
        """Start audio recording."""
        if self.stream is not None:
            logger.warning("Audio stream already running")
            return
        
        try:
            # Get default input device
            device_info = sd.query_devices(kind='input')
            logger.info(f"Using audio device: {device_info['name']}")
            
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                blocksize=self.blocksize,
                callback=self._audio_callback
            )
            
            self.stream.start()
            self.is_recording = True
            logger.info("Audio recording started")
            
        except Exception as e:
            logger.error(f"Failed to start audio recording: {e}")
            raise
    
    def stop(self):
        """Stop audio recording."""
        if self.stream is None:
            logger.warning("No audio stream to stop")
            return
        
        try:
            self.is_recording = False
            self.stream.stop()
            self.stream.close()
            self.stream = None
            logger.info("Audio recording stopped")
            
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
    
    def list_devices(self):
        """List available audio devices."""
        devices = sd.query_devices()
        logger.info("Available audio devices:")
        for i, device in enumerate(devices):
            logger.info(f"  [{i}] {device['name']} (in: {device['max_input_channels']}, out: {device['max_output_channels']})")
        return devices
