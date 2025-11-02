# Guide d'utilisation du Viewer 3D Autodesk Forge

## 🎨 Vue d'ensemble

Le viewer 3D intégré permet de visualiser vos modèles BIM directement dans l'application Smart Clash Reporter et de localiser précisément les clashes.

## ✨ Fonctionnalités

### Chargement automatique
- Les modèles se chargent automatiquement depuis les URNs des clashes
- Affichage de l'état de chargement en temps réel
- Support multi-modèles

### Contrôles viewer
- **🎯 Ajuster** : Ajuste la vue pour voir tous les modèles
- **🔄 Réinitialiser** : Réinitialise la vue et les couleurs
- **👁️ X-Ray** : Active/désactive le mode transparence

### Navigation 3D
- **Rotation** : Clic gauche + glisser
- **Pan** : Clic droit + glisser  
- **Zoom** : Molette de la souris
- **Sélection** : Clic sur un élément

### Localisation des clashes
1. Sélectionnez un clash dans le tableau
2. Le viewer zoome automatiquement sur le clash
3. Les éléments en conflit sont colorés :
   - 🔴 **Rouge** : Élément A
   - 🔵 **Bleu** : Élément B

## 🔧 Configuration technique

### Endpoints API

#### GET /api/viewer/token
Récupère un token d'accès pour le viewer Autodesk.

**Réponse**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### GET /api/viewer/model-urns
Récupère les URNs des modèles depuis les clashes actuels.

**Réponse**:
```json
{
  "urns": [
    "urn:dXJuOmFkc2sud2lwcHJvZDpm...",
    "urn:dXJuOmFkc2sud2lwcHJvZDpm..."
  ],
  "count": 2
}
```

#### GET /api/viewer/clash/{clash_id}
Récupère les données d'un clash spécifique pour le viewer.

**Réponse**:
```json
{
  "clash_id": "123",
  "element_a": {
    "urn": "urn:...",
    "guid": "abc-123",
    "name": "Wall-001"
  },
  "element_b": {
    "urn": "urn:...",
    "guid": "def-456",
    "name": "Beam-002"
  },
  "location": {
    "x": 10.5,
    "y": 20.3,
    "z": 5.7
  }
}
```

## 📋 Workflow d'utilisation

### Étape 1 : Charger les données
```
1. Lancez l'application en mode LIVE
2. Authentifiez-vous avec Autodesk
3. Cliquez sur "🔄 Charger les clashes depuis ACC"
```

### Étape 2 : Visualiser les modèles
```
1. Scrollez jusqu'à la section "🎨 Visualisation 3D"
2. Attendez le chargement automatique des modèles
3. Utilisez les contrôles pour naviguer
```

### Étape 3 : Localiser un clash
```
1. Trouvez un clash dans le tableau
2. Notez son ID
3. Le viewer zoomera automatiquement dessus
4. Les éléments seront colorés en rouge et bleu
```

## 🔍 Détails techniques

### Architecture
```
Frontend (Streamlit)
    ↓
viewer_component.html (iframe)
    ↓
Autodesk Forge Viewer API
    ↓
Backend FastAPI (/api/viewer/*)
    ↓
APS Model Coordination API
```

### Composants

#### viewer_component.html
- Viewer HTML/JavaScript standalone
- Communication via `postMessage` avec Streamlit
- Gestion des tokens et URNs
- Coloration et isolation des éléments

#### routes_viewer.py
- Endpoints FastAPI pour le viewer
- Récupération des tokens APS
- Extraction des URNs depuis les clashes
- Mapping clash → viewable data

#### streamlit_app.py
- Intégration iframe du viewer
- Communication bidirectionnelle
- Synchronisation tableau ↔ viewer

## 🐛 Dépannage

### Le viewer ne se charge pas
1. Vérifiez que le token APS est valide
2. Vérifiez les URNs des modèles
3. Consultez la console navigateur (F12)

### Les modèles ne s'affichent pas
1. Vérifiez que les modèles ont été traduits dans APS
2. Vérifiez que les URNs sont corrects
3. Vérifiez les permissions sur les modèles

### Le zoom sur clash ne fonctionne pas
1. Vérifiez que le clash_id est correct
2. Vérifiez que les GUIDs sont présents
3. Consultez les logs backend

## 📚 Ressources

- [Autodesk Forge Viewer](https://forge.autodesk.com/en/docs/viewer/v7/)
- [APS Model Coordination API](https://aps.autodesk.com/en/docs/acc/v1/)
- [Streamlit Components](https://docs.streamlit.io/library/components)

## ⚡ Limitations connues

- Le matching GUID → dbId est simplifié
- Support limité pour les modèles très volumineux
- Le cache des tokens expire après 1h

## 🚀 Améliorations futures

- [ ] Cache des modèles chargés
- [ ] Sélection multiple de clashes
- [ ] Mesure des distances
- [ ] Capture d'écran intégrée
- [ ] Annotations 3D
- [ ] Partage de vues
