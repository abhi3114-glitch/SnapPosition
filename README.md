# SnapPosition

Behavioral Mouse Movement Heatmap and Personality Visualizer

A desktop tool that captures mouse movement patterns including speed, hesitation zones, acceleration bursts, and clicks, then generates personality-style visualizations for behavioral analysis.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Visualizations](#visualizations)
- [Data Model](#data-model)
- [Project Structure](#project-structure)
- [Privacy](#privacy)
- [Technical Stack](#technical-stack)
- [Troubleshooting](#troubleshooting)

---

## Features

### Mouse Event Capture
- Real-time position tracking with configurable sample rate
- Speed calculation between consecutive positions (pixels per second)
- Click event detection and logging
- Thread-safe data collection using pynput

### Data Analysis
- Movement density computation across screen regions
- Hesitation zone detection based on dwell time and low speed
- Acceleration burst identification for sudden speed changes
- Comprehensive statistical analysis (mean, max, standard deviation)

### Visualizations
- Movement density heatmap with logarithmic scaling
- Hesitation zones map highlighting areas of mouse lingering
- Speed distribution histogram with kernel density estimation
- Movement path trace with speed-based color coding
- Personality profile summary combining all metrics

### Export Options
- JSON export with full event data and computed statistics
- PNG image export for each visualization type
- Session metadata including timestamps and event counts

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/abhi3114-glitch/SnapPosition.git
   cd SnapPosition
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Recording a Session

1. Click the **Start** button in the sidebar to begin recording
2. Move your mouse around the screen naturally for 10-30 seconds
3. Click on various elements to record decision points
4. Click the **Stop** button to end recording and generate visualizations

### Viewing Results

After stopping a recording session, navigate through the visualization tabs:

| Tab | Description |
|-----|-------------|
| Heatmap | Movement density across screen regions |
| Hesitation | Zones where the mouse lingered or moved slowly |
| Speed | Distribution analysis of movement speeds |
| Path | Visual trace of mouse movement with speed coloring |
| Personality | Comprehensive behavioral summary |

### Exporting Data

- **JSON Export**: Download raw event data with computed statistics
- **Image Export**: Download PNG images of each visualization

---

## Visualizations

### Movement Heatmap
Displays the density of mouse positions across the screen using a color gradient. Hot spots indicate areas with frequent mouse activity.

### Hesitation Map
Highlights zones where the mouse lingered with low speed or high dwell time. Useful for identifying areas of uncertainty or careful navigation.

### Speed Distribution
Shows the distribution of movement speeds through histogram and kernel density estimation plots. Includes mean and median indicators.

### Path Trace
Visualizes the complete mouse movement path with color coding based on speed. Green marker indicates start position, red marker indicates end position.

### Personality Profile
Combines all metrics into a behavioral summary including:
- Movement Style (Fast/Balanced/Deliberate)
- Precision Level (Steady/Variable)
- Decisiveness (based on click patterns)
- Energy Level (based on acceleration bursts)

---

## Data Model

Each mouse event is stored with the following structure:

```json
{
  "x": 100,
  "y": 200,
  "speed": 450.5,
  "click": false,
  "timestamp": 1702070000.123
}
```

| Field | Type | Description |
|-------|------|-------------|
| x | int | X coordinate in pixels |
| y | int | Y coordinate in pixels |
| speed | float | Movement speed in pixels per second |
| click | bool | True if this event was a click |
| timestamp | float | Unix timestamp of the event |

### Exported JSON Structure

```json
{
  "metadata": {
    "export_time": "2024-12-08T23:30:00",
    "total_events": 1500,
    "app": "SnapPosition"
  },
  "statistics": {
    "total_events": 1500,
    "total_clicks": 12,
    "avg_speed": 450.5,
    "max_speed": 2100.0,
    "duration": 30.5,
    "distance_traveled": 15000.0
  },
  "events": [...]
}
```

---

## Project Structure

```
SnapPosition/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── logger.py            # Mouse event capture with pynput
│   ├── processor.py         # Data analysis and statistics
│   └── visualizer.py        # Matplotlib visualization generation
├── app.py                   # Streamlit web application
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

### Module Descriptions

**logger.py**
- MouseLogger class with start/stop controls
- Thread-safe event collection using locks
- Speed calculation between consecutive positions
- Configurable sample rate to manage data volume

**processor.py**
- Grid-based heatmap generation
- Hesitation detection using speed and dwell time thresholds
- Acceleration burst detection for rapid speed changes
- Statistical aggregation functions

**visualizer.py**
- Matplotlib figure generation for all visualization types
- Seaborn integration for statistical plots
- Image export utilities for PNG generation
- Personality trait calculation algorithms

---

## Privacy

This application is designed with privacy as a core principle:

- All data remains on your local machine
- No network requests are made to external servers
- No screenshots or screen content are captured
- Only mouse position coordinates are recorded
- Data exists only in memory during the session
- Exported files are saved locally under your control

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Core Language | Python 3.8+ |
| Mouse Capture | pynput |
| Web Interface | Streamlit |
| Numerical Computing | NumPy |
| Visualization | Matplotlib, Seaborn |
| Image Processing | Pillow |

---

## Troubleshooting

### Permission Issues on macOS

On macOS, accessibility permissions are required for pynput to capture mouse events. Grant permission to your terminal application in System Preferences > Security and Privacy > Privacy > Accessibility.

### High CPU Usage During Recording

If CPU usage is high during recording, increase the sample rate in the MouseLogger initialization. The default is 50ms between samples. Increase this value to reduce data volume:

```python
logger = MouseLogger(sample_rate=0.1)  # 100ms between samples
```

### Missing Visualizations After Recording

Ensure you have recorded at least 3-5 seconds of mouse movement before stopping. Very short sessions may not generate meaningful heatmaps.

### Streamlit Port Already in Use

If port 8501 is occupied, specify an alternative port:

```bash
streamlit run app.py --server.port 8502
```

---

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
