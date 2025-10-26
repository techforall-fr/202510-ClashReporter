# Contributing to Smart Clash Reporter

Merci de votre intérêt pour contribuer à Smart Clash Reporter! 🎉

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Standards de code](#standards-de-code)
- [Process de review](#process-de-review)
- [Reporting bugs](#reporting-bugs)

## Code de conduite

Ce projet adhère à un code de conduite. En participant, vous acceptez de maintenir un environnement respectueux et inclusif.

## Comment contribuer

### 1. Fork & Clone

```bash
# Fork sur GitHub, puis:
git clone https://github.com/votre-username/smart-clash-reporter.git
cd smart-clash-reporter
```

### 2. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

**Conventions de nommage:**
- `feature/` - Nouvelles fonctionnalités
- `fix/` - Corrections de bugs
- `docs/` - Modifications de documentation
- `refactor/` - Refactoring de code
- `test/` - Ajout de tests

### 3. Setup environnement

```bash
# Backend
cd backend
pip install -r requirements.txt
make dev  # Install dev dependencies

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### 4. Faire vos modifications

- Écrivez du code propre et documenté
- Ajoutez des tests si applicable
- Mettez à jour la documentation

### 5. Tester

```bash
cd backend
make test          # Run all tests
make lint          # Check code quality
make format        # Format code
```

### 6. Commit

Utilisez des messages de commit conventionnels:

```bash
git commit -m "feat: add clash filtering by category"
git commit -m "fix: correct PDF page numbering"
git commit -m "docs: update API documentation"
```

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Refactoring de code
- `test`: Ajout de tests
- `chore`: Maintenance

### 7. Push & Pull Request

```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

Puis créez une Pull Request sur GitHub avec:
- Titre descriptif
- Description détaillée des changements
- Référence aux issues liées (si applicable)
- Screenshots (si changements UI)

## Standards de code

### Python (Backend)

**Style:**
- PEP 8
- Line length: 100 caractères
- Type hints obligatoires
- Docstrings pour fonctions publiques

**Exemple:**
```python
def calculate_kpis(clashes: List[Clash]) -> KPIs:
    """
    Calculate KPIs from clash list.
    
    Args:
        clashes: List of clash objects
        
    Returns:
        Calculated KPIs
    """
    # Implementation
    pass
```

**Outils:**
- `black` - Formatting
- `ruff` - Linting
- `mypy` - Type checking

### Streamlit (Frontend)

**Style:**
- Code clair et lisible
- Commentaires pour logique complexe
- Fonctions réutilisables

### Tests

**Couverture minimale:** 70%

**Structure:**
```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected
```

### Documentation

- README.md à jour
- Docstrings pour nouvelles fonctions
- Commentaires inline pour logique complexe
- API documentation (Swagger)

## Process de review

1. **Automated checks**
   - Tests passent ✅
   - Lint sans erreurs ✅
   - Type checking OK ✅

2. **Code review**
   - Minimum 1 approbation requise
   - Réponse aux commentaires
   - Itération si nécessaire

3. **Merge**
   - Squash and merge (par défaut)
   - Delete branch après merge

## Reporting bugs

### Avant de créer une issue

- [ ] Vérifier les issues existantes
- [ ] Reproduire le bug
- [ ] Collecter les informations système

### Template d'issue

```markdown
**Description**
Description claire et concise du bug.

**Étapes pour reproduire**
1. Aller à '...'
2. Cliquer sur '...'
3. Voir l'erreur

**Comportement attendu**
Ce qui devrait se passer.

**Comportement actuel**
Ce qui se passe réellement.

**Screenshots**
Si applicable.

**Environnement:**
- OS: [e.g. Windows 11]
- Python: [e.g. 3.11.5]
- Version: [e.g. 1.0.0]

**Logs/Erreurs**
```
Coller les logs ici
```

**Contexte additionnel**
Toute information supplémentaire.
```

## Proposer des features

### Template de feature request

```markdown
**Problème à résoudre**
Description du problème ou besoin.

**Solution proposée**
Comment vous imaginez la solution.

**Alternatives considérées**
Autres approches possibles.

**Contexte additionnel**
Screenshots, mockups, etc.
```

## Questions?

- Ouvrir une discussion GitHub
- Contacter les maintainers
- Consulter la documentation

## Remerciements

Merci de contribuer à Smart Clash Reporter! 🙏

Vos contributions aident la communauté BIM à automatiser et améliorer les processus de coordination.
