# 🤝 Bijdragen aan Overheid Bekendmakingen

Bedankt voor je interesse om bij te dragen aan dit project! 

## 🧪 **BETA FEEDBACK - Heel Belangrijk!**

> ⚠️ **Dit is een bètaversie (v2024.10.04.3)** met veel nieuwe functies!  
> Jouw feedback is **cruciaal** voor een stabiele release.

### 🐛 **Bug Gevonden?**
1. Controleer [bestaande issues](https://github.com/phoenix-blue/bekendmakingen/issues)
2. [Open nieuwe issue](https://github.com/phoenix-blue/bekendmakingen/issues/new) met:
   - Home Assistant versie  
   - Integratie versie (v2024.10.04.3)
   - Logs uit Developer Tools
   - Stappen om te reproduceren

### 💡 **Suggestie of Feature?** 
- [Start een discussion](https://github.com/phoenix-blue/bekendmakingen/discussions)
- Beschrijf waarom het nuttig is
- Community kan meepraten

### ⭐ **Werkt Perfect?**
- Laat een ⭐ achter op GitHub  
- Help anderen in discussions
- Deel ervaring in HA Community

--- 

## Development Environment

### Prerequisites

- Python 3.11 or higher
- Home Assistant development environment
- Git

### Setup

1. Fork this repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/bekendmakingen.git
   cd bekendmakingen
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements_dev.txt
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

Run these before submitting:

```bash
black .
isort .
flake8
mypy custom_components/overheid_bekendmakingen
```

## Testing

```bash
pytest tests/
```

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. Push and create a Pull Request

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes  
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/modifications
- `chore:` - Maintenance tasks

## Issues

When reporting issues, please include:

- Home Assistant version
- Integration version
- Debug logs (if applicable)
- Steps to reproduce
- Expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.