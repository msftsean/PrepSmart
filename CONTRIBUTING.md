# Contributing to PrepSmart

Thank you for your interest in contributing to PrepSmart! This document provides guidelines and instructions for contributing.

## 🎯 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/msftsean/prepsmart/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your environment (OS, Python version, etc.)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain how it aligns with PrepSmart's mission
4. Consider implementation complexity

### Submitting Code

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Test thoroughly**
5. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description of what you did"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** with:
   - Description of changes
   - Link to related issue
   - Test results
   - Screenshots (if UI changes)

## 📋 Development Setup

See the [Setup Instructions](README.md#️-setup-instructions) in the README.

## 🧪 Testing

Before submitting a PR:

```bash
# Run Python tests (when available)
cd backend
pytest tests/

# Run E2E tests
npm install
npx playwright test

# Test manually
python -m src.api.app  # Backend
python -m http.server 8000  # Frontend
```

## 📝 Coding Standards

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

Example:
```python
def calculate_budget_tier(income: float, household_size: int) -> str:
    """
    Determine budget tier based on income and household size.

    Args:
        income: Monthly household income in dollars
        household_size: Number of people in household

    Returns:
        Budget tier: 'low', 'medium', or 'high'
    """
    per_person_income = income / household_size
    if per_person_income < 1000:
        return 'low'
    elif per_person_income < 3000:
        return 'medium'
    return 'high'
```

### JavaScript (Frontend)

- Use ES6+ features
- Prefer `const` over `let`, avoid `var`
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

### Documentation

- Update README.md if adding features
- Add comments for complex code
- Update API documentation if changing endpoints
- Include examples in docstrings

## 🎨 Design Principles

PrepSmart follows these core principles (see [.specify/memory/constitution.md](.specify/memory/constitution.md)):

1. **Life-Saving Priority** - Critical information first
2. **Accessibility** - Mobile-first, simple language
3. **Transparency** - Show agent progress
4. **Privacy** - Minimal data collection
5. **Budget-Conscious** - Multiple price tiers
6. **Evidence-Based** - Cite authoritative sources
7. **Speed** - Target 90-second generation
8. **Test-First** - Write tests before features
9. **Graceful Degradation** - Partial results if agents fail

All contributions should align with these principles.

## 🔒 Security

- **Never commit API keys or secrets**
- Review [SECURITY.md](SECURITY.md) before contributing
- Use `.env` for all sensitive configuration
- Validate and sanitize all user inputs
- Follow security checklist in SECURITY.md

## 🌟 Good First Issues

Look for issues labeled `good-first-issue` to get started. These are:
- Well-defined and scoped
- Good for learning the codebase
- Don't require deep architectural knowledge

## 📚 Project Structure

```
prepsmart/
├── backend/           # Python Flask backend
│   ├── src/agents/    # AI agents
│   ├── src/api/       # Flask routes
│   ├── src/models/    # Data models
│   └── src/services/  # Business logic
├── frontend/          # Static HTML/CSS/JS
│   ├── pages/         # HTML pages
│   └── assets/        # CSS, JS, images
├── docs/              # Documentation
├── tests/             # Test files
└── scripts/           # Deployment scripts
```

## 🤝 Code Review Process

1. All PRs require review before merging
2. Reviewers check for:
   - Code quality and standards
   - Test coverage
   - Documentation updates
   - Security issues
   - Performance implications
3. Address review comments
4. Maintain a respectful, constructive tone

## 📞 Getting Help

- **Documentation**: Check [docs/](docs/) folder
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions
- **Debugging**: See [docs/DEBUGGING.md](docs/DEBUGGING.md)

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Playwright Testing](https://playwright.dev/)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README acknowledgements (for major features)

---

Thank you for making PrepSmart better! Every contribution helps people prepare for crises.
