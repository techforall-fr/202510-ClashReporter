"""Chart generation for KPI visualizations."""
import io
from pathlib import Path
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt

from app.models.kpis import KPIs

# Use non-interactive backend
matplotlib.use('Agg')


def create_severity_chart(kpis: KPIs, output_path: Optional[Path] = None) -> bytes:
    """
    Create a bar chart for clash severity distribution.
    
    Args:
        kpis: KPI data
        output_path: Optional path to save the chart
        
    Returns:
        PNG image bytes
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    categories = ['Haute', 'Moyenne', 'Basse']
    values = [kpis.by_severity.high, kpis.by_severity.medium, kpis.by_severity.low]
    colors = ['#dc2626', '#f59e0b', '#10b981']
    
    ax.bar(categories, values, color=colors)
    ax.set_ylabel('Nombre de clashes')
    ax.set_title('Distribution par sévérité')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate(values):
        ax.text(i, v + max(values) * 0.02, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    image_bytes = buf.read()
    plt.close(fig)
    
    # Optionally save to file
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
    
    return image_bytes


def create_status_chart(kpis: KPIs, output_path: Optional[Path] = None) -> bytes:
    """
    Create a pie chart for clash status distribution.
    
    Args:
        kpis: KPI data
        output_path: Optional path to save the chart
        
    Returns:
        PNG image bytes
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    labels = ['Ouvert', 'Résolu', 'Supprimé']
    sizes = [kpis.by_status.open, kpis.by_status.resolved, kpis.by_status.suppressed]
    colors = ['#ef4444', '#22c55e', '#94a3b8']
    explode = (0.05, 0.05, 0)
    
    # Only show non-zero values
    filtered_data = [(l, s, c, e) for l, s, c, e in zip(labels, sizes, colors, explode) if s > 0]
    if filtered_data:
        labels, sizes, colors, explode = zip(*filtered_data)
    
    ax.pie(
        sizes, 
        labels=labels, 
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        explode=explode
    )
    ax.set_title('Distribution par statut')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    image_bytes = buf.read()
    plt.close(fig)
    
    # Optionally save to file
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
    
    return image_bytes


def create_discipline_chart(kpis: KPIs, output_path: Optional[Path] = None) -> bytes:
    """
    Create a horizontal bar chart for top discipline pairs.
    
    Args:
        kpis: KPI data
        output_path: Optional path to save the chart
        
    Returns:
        PNG image bytes
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Take top 5 discipline pairs
    top_disciplines = kpis.by_discipline[:5]
    
    if not top_disciplines:
        # Empty chart
        ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    else:
        pairs = [d.discipline_pair for d in top_disciplines]
        counts = [d.count for d in top_disciplines]
        
        y_pos = range(len(pairs))
        ax.barh(y_pos, counts, color='#3b82f6')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(pairs)
        ax.set_xlabel('Nombre de clashes')
        ax.set_title('Top 5 paires de disciplines')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(counts):
            ax.text(v + max(counts) * 0.02, i, str(v), va='center')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    image_bytes = buf.read()
    plt.close(fig)
    
    # Optionally save to file
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
    
    return image_bytes
