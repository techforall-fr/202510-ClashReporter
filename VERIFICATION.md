# ✅ Verification Checklist - Smart Clash Reporter

## 🔍 Pre-Launch Verification

Utilisez cette checklist pour vérifier que tout fonctionne avant une démo ou mise en production.

---

## 📦 Installation

- [ ] Python 3.11+ installé (`python --version`)
- [ ] Dependencies backend installées (`cd backend && pip list | grep fastapi`)
- [ ] Dependencies frontend installées (`cd frontend && pip list | grep streamlit`)
- [ ] Fichier `.env` créé (copié depuis `.env.sample`)
- [ ] Répertoires créés (`exports/`, `captures/`)

---

## 🚀 Démarrage Backend

- [ ] Backend démarre sans erreur
  ```bash
  cd backend
  python -m uvicorn app.main:app --reload
  ```
- [ ] Health check répond
  ```bash
  curl http://localhost:8000/api/health
  # Devrait retourner: {"status":"ok", "version":"1.0.0", "mode":"mock"}
  ```
- [ ] Swagger accessible: http://localhost:8000/docs
- [ ] Mode détecté correctement (MOCK ou LIVE dans les logs)

---

## 🎨 Démarrage Frontend

- [ ] Frontend démarre sans erreur
  ```bash
  cd frontend
  streamlit run streamlit_app.py
  ```
- [ ] Page accessible: http://localhost:8501
- [ ] Badge mode affiché (🟢 Mode Mock ou 🔵 ACC Live)
- [ ] Pas d'erreurs dans la console

---

## 📊 Fonctionnalités Core

### KPIs Dashboard
- [ ] 4 KPI cards s'affichent correctement
- [ ] Total clashes affiché (devrait être 100 en mode mock)
- [ ] Graphique sévérité visible (bar chart)
- [ ] Graphique statut visible (pie chart)
- [ ] Chiffres cohérents entre cards et graphiques

### Table des Clashes
- [ ] Table affiche des données
- [ ] Colonnes correctes: ID, Titre, Sévérité, Statut, Disciplines, Niveau
- [ ] Code couleur sévérité fonctionne (rouge/orange/vert)
- [ ] Pagination indiquée en bas
- [ ] Au moins 50 clashes affichés (mode mock)

### Filtres
- [ ] Filtre sévérité (sidebar) fonctionne
  - [ ] Sélectionner "Haute" → table se met à jour
  - [ ] Nombre total change
- [ ] Filtre statut fonctionne
  - [ ] Sélectionner "Ouvert" → table filtrée
- [ ] Recherche discipline fonctionne
  - [ ] Taper "MEP" → résultats filtrés
- [ ] Filtre niveau fonctionne
  - [ ] Entrer "L01" → résultats filtrés

### Export CSV
- [ ] Bouton "📥 Exporter CSV" visible
- [ ] Cliquer → fichier téléchargé
- [ ] CSV ouvreur correctement dans Excel
- [ ] Données cohérentes avec la table

### Génération PDF
- [ ] Section "Export PDF" dans sidebar
- [ ] Champs titre et "préparé par" modifiables
- [ ] Bouton "🚀 Générer PDF" cliquable
- [ ] Spinner s'affiche pendant génération
- [ ] Message "✅ Rapport généré avec succès!" apparaît
- [ ] Bouton "⬇️ Télécharger PDF" s'affiche
- [ ] Cliquer → PDF téléchargé
- [ ] PDF s'ouvre correctement
- [ ] PDF contient:
  - [ ] Page de couverture
  - [ ] Tableau KPIs
  - [ ] Graphiques (3 minimum)
  - [ ] Tableaux de clashes
  - [ ] Numéros de page
  - [ ] Disclaimer en bas

---

## 🧪 Tests Automatisés

- [ ] Tests backend passent
  ```bash
  cd backend
  pytest tests/ -v
  ```
- [ ] Tous les tests verts (0 failed)
- [ ] Couverture >70%
  ```bash
  pytest --cov=app --cov-report=html
  # Ouvrir htmlcov/index.html
  ```

---

## 🔧 Qualité Code

- [ ] Linting sans erreur
  ```bash
  cd backend
  ruff check app/
  ```
- [ ] Formatage correct
  ```bash
  black --check app/
  ```
- [ ] Type checking OK (warnings acceptables)
  ```bash
  mypy app/ --ignore-missing-imports
  ```

---

## 🐳 Docker (Optionnel)

- [ ] Build backend réussit
  ```bash
  cd backend
  docker build -t smart-clash-reporter-backend .
  ```
- [ ] Build frontend réussit
  ```bash
  cd frontend
  docker build -t smart-clash-reporter-frontend .
  ```
- [ ] docker-compose lance les services
  ```bash
  docker-compose up -d
  ```
- [ ] Services accessibles (http://localhost:8501)
- [ ] Health check backend OK
  ```bash
  docker-compose ps
  # backend devrait être "healthy"
  ```

---

## 📱 Mode Mock vs Live

### Mode Mock
- [ ] Activé automatiquement si pas de credentials
- [ ] Badge "🟢 Mode Mock" affiché
- [ ] 100 clashes générés
- [ ] Distribution réaliste:
  - [ ] ~20% high severity
  - [ ] ~50% medium severity
  - [ ] ~30% low severity
- [ ] Toutes fonctionnalités disponibles

### Mode Live (si configuré)
- [ ] Variables APS dans `.env`
- [ ] Badge "🔵 ACC Live" affiché
- [ ] Token APS obtenu (check logs backend)
- [ ] Clashes réels récupérés
- [ ] Liens ACC fonctionnels

---

## 🎬 Demo Script

- [ ] `python -m app.demo --mock` fonctionne
- [ ] Backend se lance automatiquement
- [ ] Frontend se lance automatiquement
- [ ] Navigateur s'ouvre automatiquement
- [ ] Instructions affichées clairement
- [ ] Services arrêtables avec Ctrl+C

---

## 📚 Documentation

- [ ] README.md complet et clair
- [ ] QUICKSTART.md présent
- [ ] DEMO.md avec storyboard détaillé
- [ ] API docs accessibles (/docs)
- [ ] .env.sample à jour
- [ ] Tous les endpoints documentés

---

## 🔒 Sécurité

- [ ] Aucun secret dans le code
- [ ] `.env` dans `.gitignore`
- [ ] Logs ne montrent pas les secrets
- [ ] CORS configuré correctement
- [ ] Pas de credentials hardcodés

---

## 🎯 Acceptance Criteria

| Critère | Vérifié | Notes |
|---------|---------|-------|
| Lancement < 5 min en mode mock | [ ] | Timer: ___ min |
| Export PDF fonctionnel | [ ] | Taille: ___ KB |
| Code commenté et typé | [ ] | Check docstrings |
| Aucun secret committé | [ ] | Check .gitignore |
| README clair | [ ] | Facile à suivre? |
| Tests passants | [ ] | ___ / ___ tests |

---

## 🐛 Issues Connues & Workarounds

### Issue: Port déjà utilisé
**Symptôme:** "Address already in use"
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: Module not found
**Symptôme:** "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: PDF vide ou erreur
**Symptôme:** PDF < 50KB ou erreur matplotlib
**Solution:**
```bash
pip install --upgrade reportlab matplotlib pillow
```

### Issue: Frontend ne se connecte pas au backend
**Symptôme:** "Connection refused"
**Solution:**
1. Vérifier backend lancé: `curl http://localhost:8000/api/health`
2. Vérifier `API_BASE_URL` dans frontend
3. Vérifier CORS dans backend `.env`

---

## ✅ Validation Finale

Avant de livrer ou déployer:

1. [ ] Tout fonctionne en mode mock
2. [ ] Tests automatisés passent à 100%
3. [ ] PDF généré et valide
4. [ ] CSV exporté et valide
5. [ ] Documentation à jour
6. [ ] Aucune erreur dans les logs
7. [ ] Screenshots pour démo préparés
8. [ ] Vidéo démo enregistrée (optionnel)

---

## 📊 Performance Baseline

Noter les performances pour référence:

- **Démarrage backend:** ___ secondes
- **Démarrage frontend:** ___ secondes
- **Chargement 100 clashes:** ___ ms
- **Calcul KPIs:** ___ ms
- **Génération PDF (20 clashes):** ___ secondes
- **Génération PDF (100 clashes):** ___ secondes

---

## 🎉 Prêt pour Production?

Si tous les items ci-dessus sont cochés ✅, le projet est prêt!

**Prochaines étapes:**
1. Déployer sur environnement de staging
2. Tests utilisateurs
3. Collecte feedback
4. Itération et améliorations
5. Déploiement production

---

**Date de vérification:** _______________
**Vérifié par:** _______________
**Signature:** _______________
