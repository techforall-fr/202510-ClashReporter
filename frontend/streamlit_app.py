"""Streamlit frontend for Smart Clash Reporter."""
import base64
import os
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Smart Clash Reporter",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    .kpi-label {
        font-size: 1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    .severity-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .severity-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .severity-low {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def fetch_config():
    """Fetch API configuration."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/config", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Impossible de se connecter au backend: {e}")
        return None


def fetch_kpis():
    """Fetch KPIs from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/kpis", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des KPIs: {e}")
        return None


def fetch_clashes(severity=None, status=None, discipline=None, level=None, page=1, page_size=50):
    """Fetch clashes from API."""
    try:
        params = {
            "page": page,
            "page_size": page_size,
            "sort_by": "severity",
            "sort_order": "desc"
        }
        
        if severity:
            params["severity"] = severity
        if status:
            params["status"] = status
        if discipline:
            params["discipline"] = discipline
        if level:
            params["level"] = level
        
        response = requests.get(f"{API_BASE_URL}/api/clashes", params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des clashes: {e}")
        return None


def generate_pdf_report(filters, title, prepared_by):
    """Generate PDF report."""
    try:
        payload = {
            "filters": filters,
            "title": title,
            "prepared_by": prepared_by,
            "include_screenshots": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/report/pdf",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Erreur lors de la génération du rapport: {e}")
        return None


def display_header(config):
    """Display application header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="main-header">🏗️ Smart Clash Reporter</div>', unsafe_allow_html=True)
        st.markdown("**Coordination de modèles BIM avec Autodesk ACC**")
    
    with col2:
        if config:
            mode = "🟢 Mode Mock" if config.get("is_mock_mode") else "🔵 ACC Live"
            st.markdown(f"### {mode}")


def display_kpis(kpis):
    """Display KPI cards."""
    st.markdown("### 📊 Indicateurs Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <p class="kpi-value">{kpis['total_clashes']}</p>
            <p class="kpi-label">Total Clashes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <p class="kpi-value">{kpis['by_severity']['high']}</p>
            <p class="kpi-label">Haute Sévérité</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <p class="kpi-value">{kpis['by_status']['open']}</p>
            <p class="kpi-label">Ouverts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <p class="kpi-value">{kpis['resolved_percentage']}%</p>
            <p class="kpi-label">Résolus</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Severity distribution
        severity_data = {
            "Sévérité": ["Haute", "Moyenne", "Basse"],
            "Count": [
                kpis['by_severity']['high'],
                kpis['by_severity']['medium'],
                kpis['by_severity']['low']
            ]
        }
        fig_severity = px.bar(
            severity_data,
            x="Sévérité",
            y="Count",
            title="Distribution par Sévérité",
            color="Sévérité",
            color_discrete_map={"Haute": "#dc2626", "Moyenne": "#f59e0b", "Basse": "#10b981"}
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        # Status distribution
        status_data = {
            "Statut": ["Ouvert", "Résolu", "Supprimé"],
            "Count": [
                kpis['by_status']['open'],
                kpis['by_status']['resolved'],
                kpis['by_status']['suppressed']
            ]
        }
        fig_status = px.pie(
            status_data,
            values="Count",
            names="Statut",
            title="Distribution par Statut",
            color_discrete_sequence=["#ef4444", "#22c55e", "#94a3b8"]
        )
        st.plotly_chart(fig_status, use_container_width=True)


def display_clash_table(clashes_data):
    """Display clash table with filters."""
    st.markdown("### 📋 Liste des Clashes")
    
    if not clashes_data or not clashes_data.get("clashes"):
        st.warning("Aucun clash trouvé.")
        return None
    
    clashes = clashes_data["clashes"]
    
    # Convert to DataFrame
    df_data = []
    for clash in clashes:
        df_data.append({
            "ID": clash["id"],
            "Titre": clash["title"],
            "Sévérité": clash["severity"],
            "Statut": clash["status"],
            "Disciplines": f"{clash['discipline_a']} vs {clash['discipline_b']}",
            "Niveau": clash["location"]["level"] or "N/A",
            "Élément A": clash["element_a"]["name"],
            "Élément B": clash["element_b"]["name"],
        })
    
    df = pd.DataFrame(df_data)
    
    # Style function for severity
    def style_severity(val):
        if val == "high":
            return 'background-color: #fee2e2; color: #991b1b; font-weight: bold'
        elif val == "medium":
            return 'background-color: #fef3c7; color: #92400e; font-weight: bold'
        else:
            return 'background-color: #d1fae5; color: #065f46; font-weight: bold'
    
    # Display table
    st.dataframe(
        df.style.applymap(style_severity, subset=['Sévérité']),
        use_container_width=True,
        height=400
    )
    
    # Pagination info
    total = clashes_data.get("total", 0)
    page = clashes_data.get("page", 1)
    total_pages = clashes_data.get("total_pages", 1)
    
    st.caption(f"Page {page} / {total_pages} - Total: {total} clashes")
    
    return df


def display_viewer():
    """Display Autodesk Viewer section."""
    st.markdown("### 🎨 Visualisation 3D")
    
    st.info("""
    **Note:** L'intégration complète du viewer Autodesk nécessite un token valide.
    En mode mock, un viewer de démonstration peut être affiché.
    
    Pour une démo complète:
    1. Sélectionnez un clash dans le tableau
    2. Cliquez sur "Focus" pour zoomer sur le clash
    3. Utilisez "Capture" pour enregistrer une image
    """)
    
    # Placeholder for viewer
    st.markdown("""
    <div style="background: #f3f4f6; border: 2px dashed #9ca3af; border-radius: 0.5rem; 
                padding: 3rem; text-align: center; min-height: 400px;">
        <h3 style="color: #6b7280;">Autodesk Viewer</h3>
        <p style="color: #9ca3af;">
            Le viewer 3D s'affichera ici avec un token APS valide.<br>
            Intégration via JavaScript + Autodesk Forge Viewer API
        </p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application."""
    # Initialize session state
    if 'filters' not in st.session_state:
        st.session_state.filters = {}
    
    # Fetch configuration
    config = fetch_config()
    
    # Header
    display_header(config)
    
    st.markdown("---")
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("## ⚙️ Filtres")
        
        severity_filter = st.multiselect(
            "Sévérité",
            options=["high", "medium", "low"],
            format_func=lambda x: {"high": "Haute", "medium": "Moyenne", "low": "Basse"}[x]
        )
        
        status_filter = st.multiselect(
            "Statut",
            options=["open", "resolved", "suppressed"],
            format_func=lambda x: {"open": "Ouvert", "resolved": "Résolu", "suppressed": "Supprimé"}[x]
        )
        
        discipline_filter = st.text_input("Discipline (recherche)")
        level_filter = st.text_input("Niveau")
        
        st.session_state.filters = {
            "severity": severity_filter or None,
            "status": status_filter or None,
            "discipline": discipline_filter or None,
            "level": level_filter or None
        }
        
        st.markdown("---")
        
        st.markdown("## 📄 Export PDF")
        
        report_title = st.text_input("Titre du rapport", "Rapport de Clashes")
        prepared_by = st.text_input("Préparé par", "Smart Clash Reporter")
        
        if st.button("🚀 Générer PDF", use_container_width=True, type="primary"):
            with st.spinner("Génération du rapport en cours..."):
                pdf_bytes = generate_pdf_report(
                    filters=st.session_state.filters,
                    title=report_title,
                    prepared_by=prepared_by
                )
                
                if pdf_bytes:
                    st.success("✅ Rapport généré avec succès!")
                    st.download_button(
                        label="⬇️ Télécharger PDF",
                        data=pdf_bytes,
                        file_name="clash_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    
    # Main content
    # Fetch KPIs
    kpis = fetch_kpis()
    if kpis:
        display_kpis(kpis)
    
    st.markdown("---")
    
    # Fetch clashes
    clashes_data = fetch_clashes(
        severity=st.session_state.filters.get("severity"),
        status=st.session_state.filters.get("status"),
        discipline=st.session_state.filters.get("discipline"),
        level=st.session_state.filters.get("level")
    )
    
    if clashes_data:
        df = display_clash_table(clashes_data)
        
        # Export CSV
        if df is not None and not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exporter CSV",
                data=csv,
                file_name="clashes.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    # Viewer section
    display_viewer()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
        <p>Smart Clash Reporter v1.0 | Powered by Autodesk ACC + FastAPI + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
