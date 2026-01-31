"""
GhostType - Main entry point

Offline voice-to-text application with keyboard injection.
"""

import logging
import sys
import signal
from pathlib import Path

from src.config import Config
from src.core.controller import Controller


def setup_logging(config: Config):
    """Configure logging based on config."""
    log_level = config.get('system.log_level', 'INFO')
    log_file = config.get('system.log_file', 'ghosttype.log')
    
    # Create logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at {log_level} level")
    logger.info(f"Log file: {log_file}")
    
    return logger


def main():
    """Main application entry point."""
    # Load configuration
    config = Config()
    logger = setup_logging(config)
    
    logger.info("="* 60)
    logger.info("GhostType v0.1.0 - Offline Voice-to-Text")
    logger.info("Developed by Mohamed Amansour")
    logger.info("="* 60)
    
    # Create controller
    controller = Controller()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\nShutdown signal received")
        controller.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start controller
    try:
        controller.start()
        
        # Main loop - print transcribed text to console
        logger.info("\n" + "="*60)
        logger.info("READY - Listening for hotkey")
        logger.info("="*60)
        logger.info("")
        
        while True:
            # Get text from queue
            text = controller.get_text(timeout=1.0)
            
            if text:
                print(f"\n>>> Transcribed: {text}")
                print()
    
    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        controller.stop()
        logger.info("GhostType shutdown complete")


if __name__ == "__main__":
    main()
