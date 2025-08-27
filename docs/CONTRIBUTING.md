# Contributing to Serie A Predictor

Thank you for your interest in contributing to the Serie A Predictor project!

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/SerieA_predictor.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Install development dependencies: `pip install -e .[dev]`

## Code Style

- Use Black for code formatting: `black src/`
- Use flake8 for linting: `flake8 src/`
- Follow PEP 8 guidelines
- Add type hints where appropriate

## Testing

- Write tests for new features
- Run tests with: `pytest tests/`
- Aim for >80% code coverage

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests
4. Update documentation if needed
5. Run validation: `python scripts/validate_setup.py`
6. Commit and push: `git commit -m "Add your feature" && git push origin feature/your-feature-name`
7. Create a Pull Request

## Issues

- Use the issue tracker for bug reports and feature requests
- Provide detailed information and reproduction steps
- Label your issues appropriately
