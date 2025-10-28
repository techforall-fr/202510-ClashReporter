# 🚀 Démarrage en Mode LIVE - Instructions

## ✅ Vérifications préalables

Votre fichier `.env` est déjà configuré avec les credentials APS :
- `USE_MOCK=false` ✓
- Credentials APS présents ✓

## 🎯 Méthode 1 : Script Simplifié (Recommandé)

### Terminal 1 - Backend :
```powershell
.\start-live.ps1
```

### Terminal 2 - Frontend :
```powershell
cd frontend
$env:API_BASE_URL = "http://localhost:8000"
streamlit run streamlit_app.py
```

---

## 🛠️ Méthode 2 : Commandes Manuelles

### Terminal 1 - Backend :
```powershell
cd backend
$env:USE_MOCK = "false"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 - Frontend :
```powershell
cd frontend
$env:API_BASE_URL = "http://localhost:8000"
streamlit run streamlit_app.py
```

---

## 🔍 Vérifier le Mode

Une fois le backend démarré, vous verrez dans les logs :

**Mode MOCK :**
```
INFO: Mock mode enabled - using generated data
```

**Mode LIVE :**
```
INFO: Live mode enabled - connecting to APS
INFO: APS credentials validated
```

Vous pouvez aussi vérifier à :
- http://localhost:8000/docs
- Regardez la section "Application Status" qui indique le mode actif

---

## 🐛 Dépannage

### Le backend démarre en MOCK malgré tout :

1. **Vérifier les credentials dans `.env`** :
   ```powershell
   Get-Content .env | Select-String "APS_"
   ```
   
   Tous les champs suivants doivent être remplis :
   - `APS_CLIENT_ID`
   - `APS_CLIENT_SECRET`
   - `APS_ACCOUNT_ID`
   - `APS_PROJECT_ID`

2. **Forcer la variable d'environnement** :
   ```powershell
   # Avant de lancer uvicorn
   $env:USE_MOCK = "false"
   ```

3. **Vérifier la configuration** :
   Ouvrir `backend/app/core/config.py` et vérifier :
   ```python
   use_mock: bool = False  # Doit être False
   ```

### Les credentials sont rejetés :

Si vous voyez des erreurs d'authentification APS :
```
ERROR: APS authentication failed
```

Vérifiez que vos credentials sont valides sur le portail Autodesk Platform Services.

---

## 📊 URLs importantes

- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## 💡 Astuce

Pour éviter de taper les commandes à chaque fois, utilisez le script `start-live.ps1` qui force automatiquement le mode LIVE avec `$env:USE_MOCK = "false"`.
