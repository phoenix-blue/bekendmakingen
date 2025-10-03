# Contributing to Overheid Bekendmakingen

Thank you for your interest in contributing to this Home Assistant integration! 

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