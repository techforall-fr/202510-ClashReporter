"""Streamlit frontend for Smart Clash Reporter."""
import base64
import json
import os
from io import BytesIO
from datetime import datetime, timezone

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

# Internationalization
def load_locale(language="en"):
    locale_file = f"{language}.json"
    try:
        with open(locale_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Locale file {locale_file} not found")
        return {}

def detect_language():
    """Detect user language from browser."""
    # Simple detection: check if 'fr' in the browser language
    import streamlit.components.v1 as components
    # Use a small component to get browser language
    language_detector = """
    <script>
        const lang = navigator.language || navigator.userLanguage;
        window.parent.postMessage({'type': 'LANGUAGE_DETECTED', 'language': lang}, '*');
    </script>
    """
    components.html(language_detector, height=0)

    # For demonstration, assume English, but in real app, would need session state
    # For simplicity, let's default to 'en' and allow override
    return "en"

# Detect user language (fr or en)
def get_user_language():
    """Get user language from browser if possible, fallback to environment."""
    query_params = st.experimental_get_query_params()
    lang = query_params.get("lang", [None])[0]

    if lang and lang in ["fr", "en"]:
        return lang

    # Check environment for server language
    env_lang = os.environ.get("LANG", "").lower()
    if "fr" in env_lang:
        return "fr"

    # Default to English
    return "en"

# Initialize language in session state
if "language" not in st.session_state:
    # For automatic detection, we'll use a placeholder
    st.session_state.language = "en"  # Default, will be overridden by detection

user_language = st.session_state.language
LOCALE = load_locale(user_language)

def tr(key_path):
    keys = key_path.split('.')
    value = LOCALE
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return key_path  # fallback
    return value

# Page config with JavaScript for language detection
st.set_page_config(
    page_title="Smart Clash Reporter",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Language detection JavaScript
st.markdown("""
<script>
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('lang')) {
        const browserLang = navigator.language || navigator.userLanguage;
        const isFrench = browserLang.toLowerCase().startsWith('fr');
        const lang = isFrench ? 'fr' : 'en';
        const newUrl = window.location.pathname + '?lang=' + lang + window.location.hash;
        window.history.replaceState({}, '', newUrl);
        window.location.reload();
    }
</script>
""", unsafe_allow_html=True)

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
        st.error(tr("errors.backend_connection").format(error=str(e)))
        return None


def fetch_auth_status():
    """Fetch authentication status."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/status", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"authenticated": False, "user_token_available": False}


def display_auth_status(config, auth_status):
    """Display authentication status and login button."""
    if config and not config.get("is_mock_mode"):
        if auth_status.get("authenticated"):
            st.success("✅ Connecté avec un compte Autodesk")
            if st.button("🚪 Se déconnecter", key="logout"):
                try:
                    requests.get(f"{API_BASE_URL}/api/auth/logout", timeout=5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la déconnexion: {e}")
        else:
            st.warning("⚠️ Mode LIVE nécessite une authentification Autodesk")
            st.markdown("""
            Pour accéder aux données réelles de votre projet ACC/BIM 360, vous devez vous connecter avec votre compte Autodesk.
            """)
            if st.button("🔐 Se connecter avec Autodesk", type="primary", key="login"):
                login_url = f"{API_BASE_URL}/api/auth/login"
                st.markdown(f'<meta http-equiv="refresh" content="0;url={login_url}">', unsafe_allow_html=True)


def fetch_kpis():
    """Fetch KPIs from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/kpis", timeout=300)
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
        
        response = requests.get(f"{API_BASE_URL}/api/clashes", params=params, timeout=300)
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
            timeout=300
        )
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Erreur lors de la génération du rapport: {e}")
        return None


def fetch_problems(clash_id=None):
    """Fetch problems from API, optionally filtered by clash."""
    try:
        params = {}
        if clash_id:
            params["clash_id"] = clash_id
        response = requests.get(f"{API_BASE_URL}/api/problems", params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des problèmes: {e}")
        return None


def create_problem_api(title, description, status, priority, clash_id, assigned_to=None, due_date=None):
    """Create a new problem linked to a clash."""
    payload = {
        "title": title,
        "description": description or None,
        "status": status,
        "priority": priority,
        "clash_id": clash_id
    }
    if assigned_to:
        payload["assigned_to"] = assigned_to
    if due_date:
        payload["due_date"] = due_date

    response = requests.post(f"{API_BASE_URL}/api/problems", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def link_problem_api(problem_id, clash_id):
    """Link an existing problem to a clash."""
    payload = {"clash_id": clash_id}
    response = requests.post(f"{API_BASE_URL}/api/problems/{problem_id}/link", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def unlink_problem_api(problem_id, clash_id):
    """Remove the clash reference from a problem."""
    payload = {"clash_id": clash_id}
    response = requests.delete(f"{API_BASE_URL}/api/problems/{problem_id}/link", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


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


def display_problems_panel(selected_clash_id):
    """Display problems linked to a clash and provide management actions."""
    st.markdown("### 🛠️ Problèmes liés au clash")
    
    if not selected_clash_id:
        st.info("Sélectionnez un clash pour consulter ou créer des problèmes associés.")
        return
    
    problems_response = fetch_problems(selected_clash_id)
    problems = problems_response.get("problems", []) if problems_response else []

    # Summary of overdue problems
    if problems:
        overdue_entries = []
        now = datetime.now(timezone.utc)
        for problem in problems:
            due_date_value = problem.get("due_date")
            if not due_date_value:
                continue
            try:
                due_date = datetime.fromisoformat(due_date_value.replace("Z", "+00:00"))
            except ValueError:
                continue

            if due_date < now and problem.get("assigned_to"):
                overdue_entries.append(
                    {
                        "Titre": problem.get("title"),
                        "Assigné à": problem.get("assigned_to"),
                        "Échéance": due_date.strftime("%d/%m/%Y"),
                        "Statut": problem.get("status", "").replace("_", " ").title(),
                    }
                )

        if overdue_entries:
            st.markdown("#### ⏰ Problèmes assignés en retard")
            df_overdue = pd.DataFrame(overdue_entries)
            st.dataframe(df_overdue, use_container_width=True)

    if problems:
        for problem in problems:
            header = f"{problem['title']} • {problem['status'].replace('_', ' ').title()}"
            with st.expander(header, expanded=False):
                st.write(problem.get("description") or "Pas de description.")
                meta_cols = st.columns(2)
                meta_cols[0].markdown(f"**Priorité :** {problem['priority'].capitalize()}")
                meta_cols[1].markdown(f"**ID :** `{problem['id']}`")
                
                if st.button("Retirer le lien avec ce clash", key=f"unlink-{problem['id']}"):
                    try:
                        unlink_problem_api(problem["id"], selected_clash_id)
                        st.success("Lien supprimé.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Impossible de retirer le lien : {exc}")
    else:
        st.info("Aucun problème n'est lié à ce clash.")
    
    st.markdown("---")
    st.markdown("#### ➕ Créer un nouveau problème")
    with st.form(key="create-problem-form"):
        title = st.text_input("Titre", max_chars=128)
        description = st.text_area("Description", height=120)
        status = st.selectbox(
            "Statut",
            options=["open", "in_progress", "resolved", "closed"],
            format_func=lambda value: {
                "open": "Ouvert",
                "in_progress": "En cours",
                "resolved": "Résolu",
                "closed": "Fermé"
            }[value]
        )
        priority = st.selectbox(
            "Priorité",
            options=["high", "medium", "low"],
            format_func=lambda value: {
                "high": "Haute",
                "medium": "Moyenne",
                "low": "Basse"
            }[value],
            index=1
        )
        submit = st.form_submit_button("Créer et lier")
        
        if submit:
            if not title:
                st.warning("Le titre est obligatoire pour créer un problème.")
            else:
                try:
                    create_problem_api(
                        title=title,
                        description=description,
                        status=status,
                        priority=priority,
                        clash_id=selected_clash_id
                    )
                    st.success("Problème créé et lié au clash.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Impossible de créer le problème : {exc}")
    
    st.markdown("---")
    st.markdown("#### 🔗 Associer un problème existant")
    all_problems_response = fetch_problems()
    all_problems = all_problems_response.get("problems", []) if all_problems_response else []
    linkable = [p for p in all_problems if selected_clash_id not in p.get("clash_ids", [])]
    
    if linkable:
        options = {
            f"{p['title']} ({p['id']})": p['id']
            for p in linkable
        }
        selection = st.selectbox(
            "Sélectionner un problème",
            options=list(options.keys()),
            key="existing-problem-select"
        )
        if st.button("Associer ce problème", key="link-existing-problem"):
            problem_id = options.get(selection)
            if problem_id:
                try:
                    link_problem_api(problem_id, selected_clash_id)
                    st.success("Problème associé au clash.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Impossible d'associer le problème : {exc}")
    else:
        st.info("Aucun autre problème disponible pour être associé.")


def display_viewer(config=None, selected_clash_id=None):
    """Display Autodesk Viewer section with 3D models."""
    st.markdown("### 🎨 Visualisation 3D")

    st.info("""
    **Viewer Autodesk Forge** - Visualisez vos modèles BIM en 3D

    - 🔍 Les modèles se chargent automatiquement
    - 🎯 Cliquez sur un clash dans le tableau puis sur "📍 Zoomer sur ce clash" pour le localiser
    - 🎨 Les éléments en conflit sont colorés (rouge et bleu)
    """)

    has_credentials = bool(config and config.get("has_aps_credentials"))
    is_mock_mode = bool(config and config.get("is_mock_mode"))

    if not has_credentials:
        st.warning(
            "Le viewer Autodesk nécessite des identifiants APS valides. "
            "Ajoutez vos secrets APS dans le backend (.env) puis redémarrez pour activer la visualisation 3D."
        )
        return

    if is_mock_mode:
        st.info(
            "Le viewer n'est pas disponible en mode mock. "
            "Basculez en mode live avec des identifiants APS valides pour activer la visualisation 3D."
        )
        return

    # Load viewer HTML
    viewer_html_path = "viewer_component.html"
    try:
        with open(viewer_html_path, 'r', encoding='utf-8') as f:
            viewer_html = f.read()
        
        # Inject API URL
        viewer_html = viewer_html.replace(
            "const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000';",
            f"const API_BASE_URL = '{API_BASE_URL}';"
        )
        
        # Embed the viewer
        st.components.v1.html(viewer_html, height=650, scrolling=False)
        
        # Focus button if clash is selected
        if selected_clash_id:
            st.markdown(f"""
            <script>
                // Send message to iframe to focus on clash
                const iframe = window.parent.document.querySelector('iframe');
                if (iframe && iframe.contentWindow) {{
                    iframe.contentWindow.postMessage({{
                        type: 'FOCUS_CLASH',
                        clashId: '{selected_clash_id}'
                    }}, '*');
                }}
            </script>
            """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error("⚠️ Fichier viewer_component.html introuvable")
        st.markdown("""
        <div style="background: #f3f4f6; border: 2px dashed #9ca3af; border-radius: 0.5rem; 
                    padding: 3rem; text-align: center; min-height: 400px;">
            <h3 style="color: #6b7280;">Autodesk Viewer</h3>
            <p style="color: #9ca3af;">
                Le composant viewer est manquant.<br>
                Vérifiez que viewer_component.html existe dans le répertoire frontend.
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
        # Authentication status (only in LIVE mode)
        auth_status = fetch_auth_status()
        display_auth_status(config, auth_status)
        
        # Refresh button (only in LIVE mode when authenticated)
        if config and not config.get("is_mock_mode") and auth_status.get("authenticated"):
            if st.button("🔄 Charger les clashes depuis ACC", use_container_width=True, type="secondary"):
                with st.spinner("Chargement des données depuis ACC..."):
                    try:
                        response = requests.post(f"{API_BASE_URL}/api/clashes/refresh", timeout=300)
                        response.raise_for_status()
                        result = response.json()
                        st.success(f"✅ {result['message']} - {result['count']} clashes chargés")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors du rafraîchissement: {e}")
        
        st.markdown("---")
        
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
    
    selected_clash_id = st.session_state.get("selected_clash_id")
    
    if clashes_data:
        df = display_clash_table(clashes_data)
        
        clash_list = clashes_data.get("clashes", [])
        if clash_list:
            st.markdown("### 🧭 Sélectionner un clash à explorer")
            option_map = {
                f"{item['id']} • {item['title']}": item['id']
                for item in clash_list
            }
            option_keys = list(option_map.keys())
            
            default_index = 0
            if selected_clash_id and selected_clash_id in option_map.values():
                for idx, key in enumerate(option_keys):
                    if option_map[key] == selected_clash_id:
                        default_index = idx
                        break
            
            selected_label = st.selectbox(
                "Clash",
                options=option_keys,
                index=default_index if option_keys else 0
            )
            selected_clash_id = option_map[selected_label]
            st.session_state.selected_clash_id = selected_clash_id
        else:
            st.session_state.pop("selected_clash_id", None)
            selected_clash_id = None
        
        # Export CSV
        if df is not None and not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exporter CSV",
                data=csv,
                file_name="clashes.csv",
                mime="text/csv"
            )
    else:
        st.session_state.pop("selected_clash_id", None)
        selected_clash_id = None
    
    st.markdown("---")
    
    # Problems management
    display_problems_panel(selected_clash_id)
    
    st.markdown("---")
    
    # Viewer section
    display_viewer(config=config, selected_clash_id=selected_clash_id)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
        <p>Smart Clash Reporter v1.0 | Powered by Autodesk ACC + FastAPI + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
