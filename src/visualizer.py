"""
Visualizer Module
Generates heatmaps, hesitation maps, speed distributions, and path traces.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from typing import Dict, Any, Optional, Tuple
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for Streamlit


def create_heatmap(processed_data: Dict[str, Any], 
                   figsize: Tuple[int, int] = (12, 8),
                   cmap: str = "hot") -> plt.Figure:
    """
    Create a movement density heatmap.
    
    Args:
        processed_data: Output from processor.process_data()
        figsize: Figure size tuple
        cmap: Colormap name
        
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    heatmap = processed_data["heatmap"]
    
    if heatmap.size == 0:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', 
                fontsize=16, transform=ax.transAxes)
        ax.set_title("Movement Heatmap", fontsize=14, fontweight='bold')
        return fig
    
    # Apply log scaling for better visualization
    heatmap_log = np.log1p(heatmap)
    
    im = ax.imshow(heatmap_log, cmap=cmap, aspect='auto', 
                   interpolation='gaussian', origin='upper')
    
    plt.colorbar(im, ax=ax, label='Movement Density (log scale)')
    
    ax.set_title("Mouse Movement Heatmap", fontsize=14, fontweight='bold')
    ax.set_xlabel("X Grid Position")
    ax.set_ylabel("Y Grid Position")
    
    plt.tight_layout()
    return fig


def create_hesitation_map(processed_data: Dict[str, Any],
                          figsize: Tuple[int, int] = (12, 8),
                          cmap: str = "YlOrRd") -> plt.Figure:
    """
    Create a hesitation zones heatmap.
    
    Args:
        processed_data: Output from processor.process_data()
        figsize: Figure size tuple
        cmap: Colormap name
        
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    hesitation_map = processed_data["hesitation_map"]
    
    if hesitation_map.size == 0:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center',
                fontsize=16, transform=ax.transAxes)
        ax.set_title("Hesitation Map", fontsize=14, fontweight='bold')
        return fig
    
    im = ax.imshow(hesitation_map, cmap=cmap, aspect='auto',
                   interpolation='gaussian', origin='upper')
    
    plt.colorbar(im, ax=ax, label='Dwell Time (seconds)')
    
    ax.set_title("Hesitation Zones Map", fontsize=14, fontweight='bold')
    ax.set_xlabel("X Grid Position")
    ax.set_ylabel("Y Grid Position")
    
    plt.tight_layout()
    return fig


def create_speed_distribution(processed_data: Dict[str, Any],
                              figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    Create a speed distribution histogram with KDE.
    
    Args:
        processed_data: Output from processor.process_data()
        figsize: Figure size tuple
        
    Returns:
        Matplotlib Figure object
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    speeds = processed_data["speed_data"]
    
    if not speeds:
        for ax in axes:
            ax.text(0.5, 0.5, "No data available", ha='center', va='center',
                    fontsize=16, transform=ax.transAxes)
        fig.suptitle("Speed Distribution", fontsize=14, fontweight='bold')
        return fig
    
    speeds_array = np.array(speeds)
    speeds_filtered = speeds_array[speeds_array > 0]  # Remove zero speeds
    
    # Histogram
    if len(speeds_filtered) > 0:
        axes[0].hist(speeds_filtered, bins=50, color='steelblue', 
                     edgecolor='white', alpha=0.7)
        axes[0].axvline(np.mean(speeds_filtered), color='red', 
                        linestyle='--', label=f'Mean: {np.mean(speeds_filtered):.1f}')
        axes[0].axvline(np.median(speeds_filtered), color='orange',
                        linestyle='--', label=f'Median: {np.median(speeds_filtered):.1f}')
    
    axes[0].set_title("Speed Histogram", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Speed (pixels/second)")
    axes[0].set_ylabel("Frequency")
    axes[0].legend()
    
    # KDE Plot
    if len(speeds_filtered) > 1:
        sns.kdeplot(speeds_filtered, ax=axes[1], fill=True, color='steelblue')
    
    axes[1].set_title("Speed Density (KDE)", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Speed (pixels/second)")
    axes[1].set_ylabel("Density")
    
    plt.tight_layout()
    return fig


def create_path_trace(processed_data: Dict[str, Any],
                      figsize: Tuple[int, int] = (12, 8),
                      show_clicks: bool = True) -> plt.Figure:
    """
    Create a mouse movement path trace visualization.
    
    Args:
        processed_data: Output from processor.process_data()
        figsize: Figure size tuple
        show_clicks: Whether to show click positions
        
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    path = processed_data["path"]
    click_positions = processed_data["click_positions"]
    speeds = processed_data["speed_data"]
    
    if not path:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center',
                fontsize=16, transform=ax.transAxes)
        ax.set_title("Movement Path", fontsize=14, fontweight='bold')
        return fig
    
    # Extract x and y coordinates
    x_coords = [p[0] for p in path]
    y_coords = [p[1] for p in path]
    
    # Create color gradient based on speed
    if speeds and len(speeds) == len(path):
        norm = mcolors.Normalize(vmin=min(speeds), vmax=max(speeds))
        cmap = plt.cm.viridis
        
        for i in range(len(path) - 1):
            color = cmap(norm(speeds[i]))
            ax.plot([x_coords[i], x_coords[i+1]], 
                   [y_coords[i], y_coords[i+1]], 
                   color=color, linewidth=1, alpha=0.7)
        
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, label='Speed (px/s)')
    else:
        ax.plot(x_coords, y_coords, color='steelblue', linewidth=1, alpha=0.7)
    
    # Mark start and end
    if path:
        ax.scatter([path[0][0]], [path[0][1]], color='green', s=100, 
                   zorder=5, label='Start', marker='o')
        ax.scatter([path[-1][0]], [path[-1][1]], color='red', s=100,
                   zorder=5, label='End', marker='s')
    
    # Show click positions
    if show_clicks and click_positions:
        click_x = [p[0] for p in click_positions]
        click_y = [p[1] for p in click_positions]
        ax.scatter(click_x, click_y, color='yellow', s=50, zorder=4,
                   label='Clicks', marker='*', edgecolors='black')
    
    ax.set_title("Mouse Movement Path", fontsize=14, fontweight='bold')
    ax.set_xlabel("X Position (pixels)")
    ax.set_ylabel("Y Position (pixels)")
    ax.invert_yaxis()  # Match screen coordinates
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    return fig


def create_personality_summary(processed_data: Dict[str, Any],
                               figsize: Tuple[int, int] = (14, 10)) -> plt.Figure:
    """
    Create a comprehensive personality-style summary visualization.
    
    Args:
        processed_data: Output from processor.process_data()
        figsize: Figure size tuple
        
    Returns:
        Matplotlib Figure object
    """
    fig = plt.figure(figsize=figsize)
    
    # Create grid layout
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    stats = processed_data["stats"]
    
    # 1. Heatmap (top left, spans 2 columns)
    ax1 = fig.add_subplot(gs[0, :2])
    heatmap = processed_data["heatmap"]
    if heatmap.size > 0:
        im = ax1.imshow(np.log1p(heatmap), cmap='hot', aspect='auto', 
                        interpolation='gaussian')
        plt.colorbar(im, ax=ax1, label='Density')
    ax1.set_title("Movement Density", fontsize=12, fontweight='bold')
    
    # 2. Stats panel (top right)
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('off')
    
    stats_text = (
        f"📊 Session Statistics\n"
        f"{'─' * 25}\n"
        f"Total Events: {stats['total_events']:,}\n"
        f"Total Clicks: {stats['total_clicks']}\n"
        f"Duration: {stats['duration']:.1f}s\n"
        f"Distance: {stats['distance_traveled']:,.0f}px\n"
        f"{'─' * 25}\n"
        f"Avg Speed: {stats['avg_speed']:.1f} px/s\n"
        f"Max Speed: {stats['max_speed']:.1f} px/s\n"
        f"Speed Std: {stats['speed_std']:.1f}\n"
        f"Accel Bursts: {stats['acceleration_bursts']}"
    )
    ax2.text(0.1, 0.9, stats_text, transform=ax2.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 3. Speed distribution (bottom left)
    ax3 = fig.add_subplot(gs[1, 0])
    speeds = processed_data["speed_data"]
    if speeds:
        speeds_filtered = [s for s in speeds if s > 0]
        if speeds_filtered:
            ax3.hist(speeds_filtered, bins=30, color='steelblue', 
                     edgecolor='white', alpha=0.7)
    ax3.set_title("Speed Distribution", fontsize=11, fontweight='bold')
    ax3.set_xlabel("Speed (px/s)")
    
    # 4. Hesitation map (bottom center)
    ax4 = fig.add_subplot(gs[1, 1])
    hesitation = processed_data["hesitation_map"]
    if hesitation.size > 0:
        im4 = ax4.imshow(hesitation, cmap='YlOrRd', aspect='auto',
                         interpolation='gaussian')
        plt.colorbar(im4, ax=ax4, label='Dwell (s)')
    ax4.set_title("Hesitation Zones", fontsize=11, fontweight='bold')
    
    # 5. Personality traits (bottom right)
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.axis('off')
    
    # Calculate personality traits based on data
    traits = _calculate_personality_traits(stats, speeds)
    
    trait_text = (
        f"🎯 Behavior Profile\n"
        f"{'─' * 25}\n"
        f"Movement Style: {traits['style']}\n"
        f"Precision: {traits['precision']}\n"
        f"Decisiveness: {traits['decisiveness']}\n"
        f"Energy Level: {traits['energy']}"
    )
    ax5.text(0.1, 0.9, trait_text, transform=ax5.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    fig.suptitle("SnapPosition - Mouse Movement Personality Analysis", 
                 fontsize=14, fontweight='bold', y=0.98)
    
    return fig


def _calculate_personality_traits(stats: Dict[str, Any], 
                                   speeds: list) -> Dict[str, str]:
    """Calculate personality traits from movement statistics."""
    avg_speed = stats.get("avg_speed", 0)
    speed_std = stats.get("speed_std", 0)
    clicks = stats.get("total_clicks", 0)
    events = stats.get("total_events", 1)
    bursts = stats.get("acceleration_bursts", 0)
    
    # Movement style
    if avg_speed > 800:
        style = "⚡ Fast & Direct"
    elif avg_speed > 400:
        style = "🎯 Balanced"
    else:
        style = "🐢 Deliberate"
    
    # Precision (based on speed variance)
    if speed_std < 200:
        precision = "🎯 High (Steady)"
    elif speed_std < 500:
        precision = "📊 Medium"
    else:
        precision = "🌊 Variable"
    
    # Decisiveness (clicks per event ratio)
    click_ratio = clicks / events if events > 0 else 0
    if click_ratio > 0.1:
        decisiveness = "⚡ Quick Decider"
    elif click_ratio > 0.05:
        decisiveness = "🤔 Thoughtful"
    else:
        decisiveness = "👁️ Observer"
    
    # Energy level
    if bursts > 10:
        energy = "🔥 High Energy"
    elif bursts > 5:
        energy = "⚡ Moderate"
    else:
        energy = "😌 Calm"
    
    return {
        "style": style,
        "precision": precision,
        "decisiveness": decisiveness,
        "energy": energy
    }


def fig_to_bytes(fig: plt.Figure, format: str = "png", dpi: int = 150) -> bytes:
    """Convert matplotlib figure to bytes for export."""
    buf = BytesIO()
    fig.savefig(buf, format=format, dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buf.seek(0)
    return buf.getvalue()
