"""
Data Processor Module
Analyzes raw mouse data for speed, hesitation zones, and acceleration patterns.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from collections import defaultdict


def process_data(data: List[Dict[str, Any]], grid_size: int = 50) -> Dict[str, Any]:
    """
    Process raw mouse data into analytics.
    
    Args:
        data: List of mouse events with x, y, speed, click, timestamp
        grid_size: Size of grid cells for heatmap generation
        
    Returns:
        Dictionary containing processed analytics
    """
    if not data:
        return {
            "heatmap": np.array([]),
            "hesitation_map": np.array([]),
            "speed_data": [],
            "click_positions": [],
            "path": [],
            "stats": _empty_stats(),
            "grid_size": grid_size,
            "bounds": (0, 0, 1920, 1080)
        }
    
    # Extract coordinates and calculate bounds
    x_coords = [e["x"] for e in data]
    y_coords = [e["y"] for e in data]
    speeds = [e["speed"] for e in data]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Add padding to bounds
    padding = 50
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = max_x + padding
    max_y = max_y + padding
    
    # Create grids
    grid_width = max(1, int((max_x - min_x) / grid_size) + 1)
    grid_height = max(1, int((max_y - min_y) / grid_size) + 1)
    
    heatmap = np.zeros((grid_height, grid_width))
    hesitation_map = np.zeros((grid_height, grid_width))
    dwell_times = defaultdict(float)
    
    # Process events
    click_positions = []
    path = []
    prev_timestamp = None
    
    for event in data:
        x, y = event["x"], event["y"]
        grid_x = int((x - min_x) / grid_size)
        grid_y = int((y - min_y) / grid_size)
        
        # Ensure within bounds
        grid_x = max(0, min(grid_x, grid_width - 1))
        grid_y = max(0, min(grid_y, grid_height - 1))
        
        # Update heatmap (movement density)
        heatmap[grid_y, grid_x] += 1
        
        # Calculate dwell time for hesitation
        if prev_timestamp is not None:
            dwell = event["timestamp"] - prev_timestamp
            if event["speed"] < 100:  # Low speed indicates hesitation
                dwell_times[(grid_y, grid_x)] += dwell
                hesitation_map[grid_y, grid_x] += dwell
        
        prev_timestamp = event["timestamp"]
        
        # Track clicks
        if event["click"]:
            click_positions.append((x, y))
        
        # Build path
        path.append((x, y))
    
    # Calculate speed statistics
    stats = _calculate_stats(data, speeds)
    
    # Detect acceleration bursts
    acceleration_events = _detect_acceleration(data)
    stats["acceleration_bursts"] = len(acceleration_events)
    
    return {
        "heatmap": heatmap,
        "hesitation_map": hesitation_map,
        "speed_data": speeds,
        "click_positions": click_positions,
        "path": path,
        "stats": stats,
        "grid_size": grid_size,
        "bounds": (min_x, min_y, max_x, max_y)
    }


def _empty_stats() -> Dict[str, Any]:
    """Return empty statistics dictionary."""
    return {
        "total_events": 0,
        "total_clicks": 0,
        "avg_speed": 0,
        "max_speed": 0,
        "min_speed": 0,
        "speed_std": 0,
        "duration": 0,
        "distance_traveled": 0,
        "acceleration_bursts": 0
    }


def _calculate_stats(data: List[Dict[str, Any]], speeds: List[float]) -> Dict[str, Any]:
    """Calculate summary statistics from mouse data."""
    if not data:
        return _empty_stats()
    
    speeds_array = np.array(speeds)
    total_clicks = sum(1 for e in data if e["click"])
    
    # Calculate total distance
    total_distance = 0
    for i in range(1, len(data)):
        dx = data[i]["x"] - data[i-1]["x"]
        dy = data[i]["y"] - data[i-1]["y"]
        total_distance += np.sqrt(dx*dx + dy*dy)
    
    # Calculate duration
    if len(data) >= 2:
        duration = data[-1]["timestamp"] - data[0]["timestamp"]
    else:
        duration = 0
    
    return {
        "total_events": len(data),
        "total_clicks": total_clicks,
        "avg_speed": float(np.mean(speeds_array)) if len(speeds_array) > 0 else 0,
        "max_speed": float(np.max(speeds_array)) if len(speeds_array) > 0 else 0,
        "min_speed": float(np.min(speeds_array)) if len(speeds_array) > 0 else 0,
        "speed_std": float(np.std(speeds_array)) if len(speeds_array) > 0 else 0,
        "duration": duration,
        "distance_traveled": total_distance,
        "acceleration_bursts": 0
    }


def _detect_acceleration(data: List[Dict[str, Any]], threshold: float = 500) -> List[int]:
    """
    Detect acceleration burst events.
    
    Args:
        data: Mouse event data
        threshold: Speed change threshold to consider as acceleration burst
        
    Returns:
        List of indices where acceleration bursts occurred
    """
    bursts = []
    
    for i in range(1, len(data)):
        speed_change = abs(data[i]["speed"] - data[i-1]["speed"])
        if speed_change > threshold:
            bursts.append(i)
    
    return bursts


def get_hesitation_zones(processed_data: Dict[str, Any], top_n: int = 5) -> List[Tuple[int, int, float]]:
    """
    Get the top hesitation zones from processed data.
    
    Args:
        processed_data: Output from process_data()
        top_n: Number of top zones to return
        
    Returns:
        List of (grid_x, grid_y, dwell_time) tuples
    """
    hesitation_map = processed_data["hesitation_map"]
    if hesitation_map.size == 0:
        return []
    
    # Find top hesitation zones
    flat_indices = np.argsort(hesitation_map.flatten())[::-1][:top_n]
    zones = []
    
    for idx in flat_indices:
        y, x = np.unravel_index(idx, hesitation_map.shape)
        dwell = hesitation_map[y, x]
        if dwell > 0:
            zones.append((x, y, float(dwell)))
    
    return zones
