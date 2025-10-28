# 🏗️ Smart Clash Reporter

**Outil clé-en-main pour la coordination BIM avec Autodesk ACC/MCP**

Smart Clash Reporter est une application complète qui se connecte à Autodesk ACC (Model Coordination), récupère les clashes de modèles BIM, les visualise en 3D, et génère automatiquement des rapports PDF professionnels.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Démarrage rapide](#-démarrage-rapide)
- [Mode Mock vs Live](#-mode-mock-vs-live)
- [API Documentation](#-api-documentation)
- [Tests](#-tests)
- [Déploiement](#-déploiement)
- [Limites et évolutions](#-limites-et-évolutions)

## ✨ Fonctionnalités

### Core Features
- ✅ **Connexion Autodesk ACC** via APIs APS (OAuth 2.0)
- ✅ **Récupération de clashes** avec pagination et filtrage
- ✅ **Visualisation 3D** avec Autodesk Viewer (intégration HTML)
- ✅ **Génération PDF automatique** avec captures, métriques, graphiques
- ✅ **KPIs en temps réel** : distribution par sévérité, statut, disciplines
- ✅ **Filtrage avancé** : par sévérité, statut, discipline, niveau
- ✅ **Export CSV** des données de clashes
- ✅ **Mode mock complet** pour démo sans credentials

### Rapports PDF
- Page de couverture personnalisable
- Graphiques de distribution (sévérité, statut, disciplines)
- Tableaux détaillés par groupe de sévérité
- Captures d'écran intégrées (si disponibles)
- Liens directs vers ACC
- Pagination et table des matières

## 🏛️ Architecture

```
smart-clash-reporter/
├── backend/                  # API Python (FastAPI)
│   ├── app/
│   │   ├── api/             # Routes REST
│   │   ├── core/            # Config, logging
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Business logic
│   │   │   ├── aps_auth.py         # OAuth APS
│   │   │   ├── aps_mc_client.py    # Model Coordination client
│   │   │   ├── clashes.py          # Clash service
│   │   │   ├── kpis.py             # KPI calculations
│   │   │   ├── report_pdf.py       # PDF generation
│   │   │   ├── chart_kpis.py       # Chart generation
│   │   │   └── storage.py          # File storage
│   │   ├── mock/            # Mock data generator
│   │   └── main.py          # FastAPI app
│   ├── tests/               # Unit tests
│   ├── requirements.txt
│   └── Makefile
├── frontend/                # UI Streamlit
│   ├── streamlit_app.py
│   └── requirements.txt
├── exports/                 # PDF reports output
├── captures/                # Screenshots storage
├── .env.sample             # Environment template
└── README.md
```

### Stack Technique

**Backend:**
- Python 3.11+
- FastAPI (API REST)
- Pydantic (validation)
- httpx/requests (HTTP client)
- ReportLab (PDF generation)
- Matplotlib (charts)

**Frontend:**
- Streamlit (UI web)
- Plotly (visualisations)
- Pandas (data manipulation)

**APIs:**
- Autodesk Platform Services (APS/Forge)
- Model Coordination API

## 🚀 Installation

### Prérequis
- Python 3.11 ou supérieur
- pip ou uv/poetry
- Git

### Installation des dépendances

```bash
# Cloner le repository
git clone <repo-url>
cd smart-clash-reporter

# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### Avec Make (recommandé)

```bash
cd backend
make install        # Installation
make dev           # Installation avec outils dev (tests, lint)
```

## ⚙️ Configuration

### Variables d'environnement

Copiez `.env.sample` vers `.env` et configurez:

```bash
cp .env.sample .env
```

**Fichier `.env`:**

```ini
# Autodesk Platform Services (APS)
APS_CLIENT_ID=your_client_id
APS_CLIENT_SECRET=your_client_secret
APS_ACCOUNT_ID=your_account_id
APS_PROJECT_ID=your_project_id
APS_COORDINATION_SPACE_ID=your_coordination_space_id
APS_MODELSET_ID=your_modelset_id

# Application
USE_MOCK=true                    # false pour mode live
LOG_LEVEL=INFO
API_PORT=8000
FRONTEND_PORT=8501

# CORS
CORS_ORIGINS=http://localhost:8501,http://localhost:3000

# Storage
EXPORTS_DIR=exports
CAPTURES_DIR=captures
```

### Obtenir les credentials APS

1. Créez une app sur [Autodesk Platform Services](https://aps.autodesk.com/)
2. Notez le `Client ID` et `Client Secret`
3. Activez les scopes: `data:read`, `viewables:read`
4. Trouvez vos IDs dans ACC:
   - `Account ID`: Settings → Account Administration
   - `Project ID`: URL du projet ACC
   - `Coordination Space ID`: Model Coordination → Space ID
   - `Modelset ID`: ID du model set coordiné

## 🎯 Démarrage rapide

### Méthode 1: Script de démo (recommandé)

```bash
# Mode mock (pas besoin de credentials)
python -m app.demo --mock

# Mode live (nécessite credentials)
python -m app.demo --live
```

Le script lance automatiquement:
- ✅ Backend API (port 8000)
- ✅ Frontend Streamlit (port 8501)
- ✅ Ouverture du navigateur

### Méthode 2: Lancement manuel

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run streamlit_app.py
```

**Accès:**
- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Méthode 3: Make

```bash
cd backend
make run          # Mode normal
make run-mock     # Force mode mock
```

## 🎭 Mode Mock vs Live

### Mode Mock (par défaut)

Le mode mock est **automatiquement activé** si:
- `USE_MOCK=true` dans `.env`
- OU aucun credential APS n'est configuré

**Avantages:**
- ✅ Démo immédiate sans credentials
- ✅ 100 clashes réalistes générés
- ✅ Distribution plausible (sévérité, statut, disciplines)
- ✅ Toutes les fonctionnalités disponibles
- ✅ URN de démo Autodesk fourni

**Données générées:**
- 100 clashes avec variété de sévérités
- 6 disciplines (MEP, Structure, Architecture, etc.)
- 7 niveaux (L00 → Roof)
- Statuts: 60% open, 30% resolved, 10% suppressed
- Sévérités: 20% high, 50% medium, 30% low

### Mode Live

Activé avec credentials APS complets.

**Prérequis:**
- Client ID/Secret APS valides
- Account, Project, Coordination Space IDs
- Accès au projet ACC

**Données:**
- ✅ Clashes réels depuis ACC
- ✅ Liens directs vers ACC
- ✅ URNs de modèles réels
- ✅ Viewer 3D avec tokens valides

## 📚 API Documentation

### Endpoints principaux

#### Health & Config
```http
GET /api/health
GET /api/config
```

#### Clashes
```http
GET /api/clashes?severity=high&status=open&page=1&page_size=50
GET /api/clashes/{clash_id}
```

**Query parameters:**
- `severity`: `high`, `medium`, `low` (multiple)
- `status`: `open`, `resolved`, `suppressed` (multiple)
- `discipline`: Filtre texte partiel
- `level`: Filtre exact sur le niveau
- `sort_by`: `severity`, `status`, `updated_at`, `created_at`
- `sort_order`: `asc`, `desc`
- `page`: Numéro de page (1-indexed)
- `page_size`: Éléments par page (max 200)

#### KPIs
```http
GET /api/kpis
```

Retourne:
- Total clashes
- Distribution par sévérité/statut
- % résolus
- Top 5 catégories
- Statistiques par discipline
- Distribution par niveau

#### Viewer Token
```http
GET /api/token/viewer
```

Retourne un token pour Autodesk Viewer (ou token mock).

#### Rapports
```http
POST /api/capture
Body: {
  "clash_id": "clash_00001",
  "image_data_url": "data:image/png;base64,..."
}

POST /api/report/pdf
Body: {
  "filters": {"severity": ["high"]},
  "title": "Rapport de Clashes",
  "prepared_by": "John Doe",
  "include_screenshots": true
}

GET /api/report/latest
```

### Documentation interactive

Accédez à la doc Swagger: http://localhost:8000/docs

## 🧪 Tests

### Lancer les tests

```bash
cd backend

# Tous les tests
pytest

# Avec couverture
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_clashes.py
pytest tests/test_report.py -v
```

### Tests inclus

- ✅ Récupération et filtrage des clashes
- ✅ Pagination correcte
- ✅ Calcul des KPIs
- ✅ Génération PDF (structure, taille minimum)
- ✅ Top catégories et disciplines

### Couverture

Les tests couvrent:
- Services métier (clashes, KPIs)
- Génération de rapports PDF
- Normalisation des données
- Agrégations et statistiques

## 🐳 Déploiement

### Docker Compose (optionnel)

```bash
docker-compose up -d
```

Voir `docker-compose.yml` pour la configuration.

### Production

**Recommandations:**
1. Utilisez un serveur WSGI production (gunicorn + uvicorn workers)
2. Reverse proxy (nginx) pour le frontend
3. Variables d'env sécurisées (secrets manager)
4. Logs centralisés
5. Monitoring (health checks)

**Exemple gunicorn:**
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 🔧 Développement

### Linting & Formatting

```bash
cd backend

# Format code
make format

# Lint
make lint

# Type checking
mypy app/ --ignore-missing-imports
```

### Structure des commits

Utilisez des commits conventionnels:
```
feat: Add clash filtering by level
fix: Correct PDF page numbering
docs: Update README with deployment info
```

## 📊 Limites et évolutions

### Limites connues

1. **Model Coordination API**
   - Les endpoints exacts peuvent varier selon la version APS
   - Vérifier la [documentation officielle](https://aps.autodesk.com/en/docs/acc/v1/overview/)
   - Implémenter les ajustements dans `aps_mc_client.py`

2. **Viewer 3D**
   - Intégration basique fournie
   - Focus/Isolate nécessite JavaScript custom
   - Capture côté client via canvas

3. **Performance**
   - Pagination limitée à 200 items/page
   - PDF limité à 20 clashes/sévérité pour taille raisonnable
   - Cache simple en mémoire (pas de Redis/DB)

### Évolutions possibles

**Court terme:**
- [ ] Export Excel/CSV enrichi
- [ ] Filtres par date de création/modification
- [ ] Tagging manuel de clashes
- [ ] Notifications par email

**Moyen terme:**
- [ ] Authentification utilisateurs
- [ ] Base de données (PostgreSQL)
- [ ] Cache distribué (Redis)
- [ ] Historique des rapports
- [ ] Comparaison de versions

**Long terme:**
- [ ] Machine Learning pour priorisation
- [ ] Workflow d'approbation
- [ ] Intégration Jira/Azure DevOps
- [ ] Application mobile
- [ ] Multi-projets dashboard

## 📄 Licence

Ce projet est un POC/démo. Pour usage commercial, contactez l'auteur.

## 🤝 Contribution

Les contributions sont bienvenues! Merci de:
1. Forker le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Committer (`git commit -m 'feat: Add amazing feature'`)
4. Pousser (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📞 Support

- Documentation APS: https://aps.autodesk.com/
- Issues: Ouvrez une issue GitHub
- Email: frenot.manu@gmail.com

## 👏 Remerciements

- Autodesk Platform Services
- FastAPI & Streamlit communities
- ReportLab pour la génération PDF

---

**Made with ❤️ for the BIM community**
