# 🎬 Smart Clash Reporter - Storyboard Démo

## 🎯 Objectif de la démo

Présenter Smart Clash Reporter comme un outil **clé-en-main** pour automatiser la coordination BIM et la génération de rapports de clashes depuis Autodesk ACC.

**Durée cible:** 60-90 secondes  
**Format:** Capture d'écran + voix-off ou texte overlay

---

## 📝 Script détaillé

### 🎬 Scène 1: Hook (0-5s)

**Visuel:**
- Écran noir → Fade in sur titre
- Animation de logo/titre

**Texte overlay:**
```
"Automatiser la coordination BIM
avec Autodesk ACC + Smart Clash Reporter"
```

**Voix-off (optionnel):**
> "Vous passez des heures à générer des rapports de clashes manuellement?"

---

### 🎬 Scène 2: Dashboard KPIs (5-15s)

**Visuel:**
- Ouverture de l'application (http://localhost:8501)
- Affichage du header avec badge "Mode Mock"
- Zoom sur les 4 KPI cards qui s'affichent progressivement:
  - Total Clashes: **100**
  - Haute Sévérité: **20**
  - Ouverts: **60**
  - % Résolus: **30%**

**Actions:**
- Les cartes apparaissent avec une animation slide-in
- Survol rapide des graphiques (bars + pie chart)

**Texte overlay:**
```
"Visualisez instantanément vos métriques clés"
```

**Voix-off (optionnel):**
> "Smart Clash Reporter récupère automatiquement vos clashes depuis ACC et affiche les métriques essentielles."

---

### 🎬 Scène 3: Table des clashes (15-30s)

**Visuel:**
- Scroll dans la table des clashes
- Highlight des colonnes importantes:
  - ID, Titre, Sévérité (couleurs: rouge/orange/vert)
  - Disciplines
  - Niveau

**Actions:**
1. Appliquer un filtre "Haute sévérité" dans la sidebar
2. La table se met à jour instantanément (100 → 20 clashes)
3. Survol d'une ligne de clash

**Texte overlay:**
```
"Filtrez par sévérité, statut, discipline ou niveau"
```

**Voix-off (optionnel):**
> "Filtrez rapidement pour vous concentrer sur les clashes critiques."

---

### 🎬 Scène 4: Clic sur un clash → Focus 3D (30-45s)

**Visuel:**
- Section "Visualisation 3D" en dessous de la table
- Placeholder du viewer avec texte explicatif
- (En production: montrer le viewer Autodesk chargé)

**Actions:**
1. Sélectionner un clash dans la table (surbrillance)
2. Montrer boutons d'action:
   - 🎯 Focus
   - 👁️ Isolate
   - 📸 Capture

**Note:**
En mode mock, afficher un message:
```
"Autodesk Viewer s'affichera ici avec un token APS valide
→ Zoom automatique sur le clash sélectionné"
```

**Texte overlay:**
```
"Localisez les clashes en 3D d'un simple clic"
```

**Voix-off (optionnel):**
> "Chaque clash peut être visualisé en 3D avec zoom automatique sur la zone de conflit."

---

### 🎬 Scène 5: Export PDF (45-65s)

**Visuel:**
- Retour à la sidebar
- Section "Export PDF"

**Actions:**
1. Remplir les champs:
   - Titre: "Rapport de Clashes - Projet Demo"
   - Préparé par: "Équipe BIM"
2. **Cliquer sur le bouton principal "🚀 Générer PDF"**
3. Spinner de chargement (2-3s)
4. ✅ Message "Rapport généré avec succès!"
5. Bouton "⬇️ Télécharger PDF" apparaît

**Texte overlay:**
```
"Générez un rapport PDF complet en un clic"
```

**Voix-off (optionnel):**
> "Générez instantanément un rapport PDF professionnel avec tous les détails."

---

### 🎬 Scène 6: Aperçu du PDF (65-85s)

**Visuel:**
- Ouverture rapide du PDF généré
- Scroll à travers les sections:
  1. **Page de garde** (titre, date, logo)
  2. **Section KPIs** avec graphiques (bars, pie charts)
  3. **Tableaux de clashes** groupés par sévérité
  4. **Captures d'écran** (si disponibles)
  5. **Liens ACC** pour chaque clash

**Actions:**
- Scroll smooth à travers 3-4 pages
- Zoom sur un graphique
- Zoom sur un tableau de clashes avec détails

**Texte overlay:**
```
"Rapport complet: KPIs, graphiques, détails, liens ACC"
```

**Voix-off (optionnel):**
> "Le rapport inclut toutes les métriques, graphiques, tableaux détaillés et liens directs vers ACC."

---

### 🎬 Scène 7: Outro (85-90s)

**Visuel:**
- Retour à l'écran titre ou logo
- Affichage des informations finales

**Texte overlay:**
```
✅ Mode mock: démo immédiate sans credentials
✅ Mode live: connexion directe à votre ACC
✅ Open-source & personnalisable

Smart Clash Reporter
github.com/[votre-repo]

Intéressé par la version PRO ?
→ Contactez-nous
```

**Voix-off (optionnel):**
> "Smart Clash Reporter: votre solution clé-en-main pour automatiser la coordination BIM. Disponible en open-source. Contactez-nous pour la version entreprise."

---

## 🎨 Notes de production

### Style visuel
- **Palette de couleurs:** Bleu professionnel (#1e40af) + accents gradient
- **Transitions:** Smooth fades et slides
- **Tempo:** Dynamique mais pas précipité
- **Musique:** Background instrumental léger (optionnel)

### Texte overlay
- **Police:** Sans-serif moderne (Inter, Roboto)
- **Taille:** Grande et lisible
- **Contraste:** Fond sombre + texte blanc OU fond clair + texte foncé
- **Animation:** Fade in + slide up

### Captures d'écran
- **Résolution:** 1920x1080 minimum
- **Format:** MP4 ou GIF haute qualité
- **Compression:** Optimisée pour web (< 10 MB)

### Points d'attention
1. **Montrer la valeur immédiate:** Gain de temps évident
2. **Simplicité:** Interface intuitive, workflow clair
3. **Résultat concret:** Le PDF final est le "wow moment"
4. **Pas de jargon technique:** Accessible aux non-devs

---

## 🎯 Variantes de démo

### Démo courte (30s) - Teaser
1. Hook (5s)
2. Dashboard KPIs (10s)
3. Clic Export PDF → Aperçu (10s)
4. Outro (5s)

### Démo technique (3-5min) - Deep dive
Inclure:
- Explication du mode mock vs live
- Démonstration des filtres avancés
- API endpoints (Swagger)
- Code walkthrough (optionnel)
- Configuration APS

### Démo live - Présentation client
- Utiliser des données réelles du projet client
- Personnaliser le rapport (logo, titre)
- Montrer l'intégration ACC réelle
- Q&A en direct

---

## 📋 Checklist avant enregistrement

- [ ] Backend lancé et fonctionnel (mode mock)
- [ ] Frontend Streamlit chargé et responsive
- [ ] Mock data générées (100 clashes)
- [ ] Graphiques s'affichent correctement
- [ ] PDF peut être généré (test)
- [ ] Résolution d'écran optimale (1920x1080)
- [ ] Navigateur en mode plein écran (F11)
- [ ] Pas de notifications/pop-ups distrayants
- [ ] Transitions fluides (60 fps)

---

## 🚀 Post-production

### Édition
1. Trim des temps morts
2. Ajout de transitions
3. Texte overlay animé
4. Color grading (optionnel)
5. Musique de fond (royalty-free)

### Export
- **Format:** MP4 (H.264)
- **Résolution:** 1080p
- **Framerate:** 30 ou 60 fps
- **Bitrate:** 8-10 Mbps

### Distribution
- **YouTube:** Titre SEO-friendly, description détaillée
- **LinkedIn:** Version courte (30-60s)
- **Site web:** Embed sur page d'accueil
- **GitHub:** Ajout au README

---

## 💡 Tips pour une démo réussie

1. **Rythme soutenu:** Pas de temps morts
2. **Focus sur le ROI:** Gain de temps, réduction d'erreurs
3. **Avant/Après:** Montrer la différence (optionnel)
4. **Call-to-Action clair:** Lien GitHub, contact, démo live
5. **Sous-titres:** Important pour accessibilité
6. **Mobile-friendly:** Version verticale pour réseaux sociaux

---

**Bon courage pour la démo! 🎬🚀**
