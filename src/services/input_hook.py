"""
Global hotkey listener using pynput.
"""

import logging
from pynput import keyboard
from typing import Callable

logger = logging.getLogger(__name__)


class InputHook:
    """
    Listens for global hotkeys and triggers callbacks.
    """
    
    def __init__(self, hotkey: str, on_press: Callable, on_release: Callable):
        """
        Initialize input hook.
        
        Args:
            hotkey: Hotkey combination (e.g., 'ctrl+alt')
            on_press: Callback when hotkey is pressed
            on_release: Callback when hotkey is released
        """
        self.hotkey = hotkey
        self.on_press_callback = on_press
        self.on_release_callback = on_release
        self.listener = None
        self.current_keys = set()
        self.hotkey_keys = self._parse_hotkey(hotkey)
        
        logger.info(f"InputHook initialized with hotkey: {hotkey}")
    
    def _parse_hotkey(self, hotkey: str) -> set:
        """
        Parse hotkey string into set of key objects.
        
        Args:
            hotkey: Hotkey string (e.g., 'ctrl+alt')
            
        Returns:
            Set of pynput Key objects
        """
        keys = set()
        parts = hotkey.lower().split('+')
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(keyboard.Key.ctrl_l)
                keys.add(keyboard.Key.ctrl_r)
            elif part == 'alt':
                keys.add(keyboard.Key.alt_l)
                keys.add(keyboard.Key.alt_r)
            elif part == 'shift':
                keys.add(keyboard.Key.shift_l)
                keys.add(keyboard.Key.shift_r)
            else:
                # Regular character key
                try:
                    keys.add(keyboard.KeyCode.from_char(part))
                except:
                    logger.warning(f"Unknown key in hotkey: {part}")
        
        return keys
    
    def _is_hotkey_pressed(self) -> bool:
        """Check if hotkey combination is currently pressed."""
        # Check if any of the required keys are pressed
        for required_key in self.hotkey_keys:
            if required_key in self.current_keys:
                return True
        return False
    
    def _on_press(self, key):
        """Internal callback for key press events."""
        self.current_keys.add(key)
        
        # Check if hotkey is now active
        if self._is_hotkey_pressed():
            try:
                self.on_press_callback()
            except Exception as e:
                logger.error(f"Error in press callback: {e}")
    
    def _on_release(self, key):
        """Internal callback for key release events."""
        was_active = self._is_hotkey_pressed()
        
        # Remove key from current set
        if key in self.current_keys:
            self.current_keys.remove(key)
        
        # Check if hotkey was released
        if was_active and not self._is_hotkey_pressed():
            try:
                self.on_release_callback()
            except Exception as e:
                logger.error(f"Error in release callback: {e}")
    
    def start(self):
        """Start listening for hotkeys."""
        if self.listener is not None:
            logger.warning("Listener already running")
            return
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            logger.info("Input hook started")
            
        except Exception as e:
            logger.error(f"Failed to start input hook: {e}")
            raise
    
    def stop(self):
        """Stop listening for hotkeys."""
        if self.listener is None:
            logger.warning("No listener to stop")
            return
        
        try:
            self.listener.stop()
            self.listener = None
            self.current_keys.clear()
            logger.info("Input hook stopped")
            
        except Exception as e:
            logger.error(f"Error stopping input hook: {e}")
