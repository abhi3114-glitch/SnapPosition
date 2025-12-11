"""
Mouse Event Logger Module
Captures mouse movements, clicks, and calculates speed using pynput.
"""

import time
import threading
from pynput import mouse
from typing import List, Dict, Any, Optional
import math


class MouseLogger:
    """Thread-safe mouse event logger using pynput."""
    
    def __init__(self, sample_rate: float = 0.05):
        """
        Initialize the mouse logger.
        
        Args:
            sample_rate: Minimum time between position samples (seconds)
        """
        self._data: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._listener: Optional[mouse.Listener] = None
        self._is_running = False
        self._sample_rate = sample_rate
        self._last_sample_time = 0
        self._last_position = (0, 0)
        self._last_timestamp = 0
        
    def _calculate_speed(self, x: int, y: int, timestamp: float) -> float:
        """Calculate speed in pixels per second."""
        if self._last_timestamp == 0:
            return 0.0
            
        time_delta = timestamp - self._last_timestamp
        if time_delta <= 0:
            return 0.0
            
        dx = x - self._last_position[0]
        dy = y - self._last_position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance / time_delta
    
    def _on_move(self, x: int, y: int):
        """Handle mouse movement events."""
        current_time = time.time()
        
        # Rate limiting to avoid too many samples
        if current_time - self._last_sample_time < self._sample_rate:
            return
            
        speed = self._calculate_speed(x, y, current_time)
        
        event = {
            "x": x,
            "y": y,
            "speed": round(speed, 2),
            "click": False,
            "timestamp": current_time
        }
        
        with self._lock:
            self._data.append(event)
            
        self._last_position = (x, y)
        self._last_timestamp = current_time
        self._last_sample_time = current_time
    
    def _on_click(self, x: int, y: int, button, pressed: bool):
        """Handle mouse click events."""
        if not pressed:
            return
            
        current_time = time.time()
        speed = self._calculate_speed(x, y, current_time)
        
        event = {
            "x": x,
            "y": y,
            "speed": round(speed, 2),
            "click": True,
            "timestamp": current_time
        }
        
        with self._lock:
            self._data.append(event)
            
        self._last_position = (x, y)
        self._last_timestamp = current_time
    
    def start(self):
        """Start capturing mouse events."""
        if self._is_running:
            return
            
        self._is_running = True
        self._last_timestamp = 0
        self._last_sample_time = 0
        
        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click
        )
        self._listener.start()
    
    def stop(self):
        """Stop capturing mouse events."""
        if not self._is_running:
            return
            
        self._is_running = False
        if self._listener:
            self._listener.stop()
            self._listener = None
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Get a copy of the captured data."""
        with self._lock:
            return list(self._data)
    
    def clear_data(self):
        """Clear all captured data."""
        with self._lock:
            self._data = []
        self._last_timestamp = 0
        self._last_position = (0, 0)
    
    def is_running(self) -> bool:
        """Check if the logger is currently running."""
        return self._is_running
    
    @property
    def event_count(self) -> int:
        """Get the number of captured events."""
        with self._lock:
            return len(self._data)


# Singleton instance for use in Streamlit
_global_logger: Optional[MouseLogger] = None


def get_logger() -> MouseLogger:
    """Get the global mouse logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = MouseLogger()
    return _global_logger
