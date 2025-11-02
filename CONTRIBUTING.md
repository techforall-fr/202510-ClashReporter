# Contributing to Smart Clash Reporter

Thank you for your interest in contributing to Smart Clash Reporter! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Code Standards](#code-standards)
- [Review Process](#review-process)
- [Reporting Bugs](#reporting-bugs)

## Code of Conduct

This project adheres to a code of conduct. By participating, you agree to maintain a respectful and inclusive environment.

## How to Contribute

### 1. Fork & Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/your-username/smart-clash-reporter.git
cd smart-clash-reporter
```

### 2. Create a Branch

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-fix
```

**Naming Conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance

### 3. Setup Environment

```bash
# Backend
cd backend
pip install -r requirements.txt
make dev  # Install dev dependencies

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### 4. Make Your Changes

- Write clean and documented code
- Add tests if applicable
- Update documentation

### 5. Test

```bash
cd backend
make test          # Run all tests
make lint          # Check code quality
make format        # Format code
```

### 6. Commit

Use conventional commit messages:

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
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

### 7. Push & Pull Request

```bash
git push origin feature/my-new-feature
```

Then create a Pull Request on GitHub with:
- Descriptive title
- Detailed description of changes
- Reference to related issues (if applicable)
- Screenshots (if UI changes)

## Code Standards

### Python (Backend)

**Style:**
- PEP 8
- Line length: 100 characters
- Type hints required
- Docstrings for public functions

**Example:**
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

**Tools:**
- `black` - Formatting
- `ruff` - Linting
- `mypy` - Type checking

### Streamlit (Frontend)

**Style:**
- Clear and readable code
- Comments for complex logic
- Reusable functions

### Tests

**Minimum Coverage:** 70%

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

- Updated README.md
- Docstrings for new functions
- Inline comments for complex logic
- API documentation (Swagger)

## Review Process

1. **Automated checks**
   - Tests pass ✅
   - Lint without errors ✅
   - Type checking OK ✅

2. **Code review**
   - Minimum 1 approval required
   - Respond to comments
   - Iterate if necessary

3. **Merge**
   - Squash and merge (default)
   - Delete branch after merge

## Reporting Bugs

### Before Creating an Issue

- [ ] Check existing issues
- [ ] Reproduce the bug
- [ ] Collect system information

### Issue Template

```markdown
**Description**
Clear and concise description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See the error

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Screenshots**
If applicable.

**Environment:**
- OS: [e.g. Windows 11]
- Python: [e.g. 3.11.5]
- Version: [e.g. 1.0.0]

**Logs/Errors**
```
Paste logs here
```

**Additional Context**
Any additional information.
```

## Suggesting Features

### Feature Request Template

```markdown
**Problem to Solve**
Description of the problem or need.

**Proposed Solution**
How you imagine the solution.

**Alternatives Considered**
Other possible approaches.

**Additional Context**
Screenshots, mockups, etc.
```

## Questions?

- Open a GitHub discussion
- Contact the maintainers
- Check the documentation

## Acknowledgments

Thank you for contributing to Smart Clash Reporter! 🙏

Your contributions help the BIM community automate and improve coordination processes.
