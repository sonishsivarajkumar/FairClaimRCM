# Contributing to FairClaimRCM

Thank you for your interest in contributing to FairClaimRCM! We welcome contributions from healthcare professionals, developers, and anyone passionate about improving healthcare technology.

## 🌟 Ways to Contribute

- **🐛 Report Bugs**: Help us identify and fix issues
- **💡 Feature Requests**: Suggest new features or improvements
- **📝 Documentation**: Improve our docs, tutorials, and examples
- **🧪 Testing**: Add test cases or improve test coverage
- **💻 Code**: Submit bug fixes, features, or performance improvements
- **🎨 Design**: Help with UI/UX improvements
- **🌍 Translation**: Help localize the project

## 🚀 Getting Started

### Prerequisites

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/fairclaimrcm.git
   cd fairclaimrcm
   ```

3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Setup

1. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

2. **Run tests to ensure everything works**:
   ```bash
   pytest
   ```

3. **Start the development server**:
   ```bash
   cd api
   uvicorn main:app --reload
   ```

## 📋 Development Guidelines

### Code Style

- **Python**: Follow PEP 8, use `black` for formatting
- **JavaScript/React**: Use Prettier and ESLint
- **Type Hints**: Use type hints for all Python functions
- **Documentation**: Document all public functions and classes

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add ICD-10 code validation endpoint
fix(core): resolve null pointer in coding engine
docs: update API documentation for v0.2
test(core): add unit tests for terminology service
```

### Testing

- **Write tests** for new features and bug fixes
- **Maintain coverage** at 80% or higher
- **Test types**: Unit tests, integration tests, API tests
- **Run tests locally** before submitting PRs

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fairclaimrcm

# Run specific test file
pytest tests/test_coding_engine.py
```

### Documentation

- **Update docs** for any new features or API changes
- **Add examples** for new functionality
- **Keep README updated** with any setup changes
- **Use clear, concise language**

## 🔧 Pull Request Process

1. **Ensure tests pass** and coverage is maintained
2. **Update documentation** as needed
3. **Lint your code**:
   ```bash
   black .
   flake8
   mypy fairclaimrcm
   ```

4. **Write a clear PR description**:
   - What does this PR do?
   - Why is this change needed?
   - How was it tested?
   - Any breaking changes?

5. **Link related issues** using keywords:
   - `Fixes #123`
   - `Closes #456`
   - `Resolves #789`

### PR Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🐛 Reporting Bugs

### Before Reporting
1. **Search existing issues** to avoid duplicates
2. **Try the latest version** to see if it's already fixed
3. **Gather information** about your environment

### Bug Report Template

```markdown
## Bug Description
Clear description of what the bug is

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen

## Screenshots
If applicable, add screenshots

## Environment
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.9.7]
- FairClaimRCM version: [e.g. 0.1.0]
- Browser (if applicable): [e.g. Chrome 96.0]

## Additional Context
Any other context about the problem
```

## 💡 Feature Requests

### Before Requesting
1. **Check existing issues** and discussions
2. **Consider the scope** - does it fit the project goals?
3. **Think about implementation** - how might it work?

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Problem/Use Case
What problem does this solve? What's the use case?

## Proposed Solution
How might this feature work?

## Alternatives
Any alternative solutions considered?

## Additional Context
Any other context, mockups, or examples
```

## 👥 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read our [Code of Conduct](CODE_OF_CONDUCT.md).

### Communication

- **Be respectful** and constructive
- **Ask questions** - we're here to help!
- **Share knowledge** - help others learn
- **Stay on topic** in discussions
- **Use clear, professional language**

### Getting Help

- **GitHub Discussions**: For questions and community chat
- **Issues**: For bug reports and feature requests
- **Discord**: Real-time community chat (link in README)
- **Email**: For private matters (contact info in README)

## 🏥 Healthcare Considerations

When contributing to healthcare-related features, please consider:

- **HIPAA Compliance**: Never include real patient data
- **Medical Accuracy**: Verify medical coding standards
- **Regulatory Requirements**: Consider FDA, CMS guidelines
- **Security**: Follow secure coding practices
- **Privacy**: Implement privacy-by-design principles

## 🎯 Good First Issues

Look for issues labeled `good-first-issue` for beginner-friendly contributions:

- Documentation improvements
- Adding test cases
- Fixing typos or formatting
- Implementing simple utility functions
- Adding configuration options

## 🚀 Advanced Contributions

For larger contributions:

1. **Open an issue first** to discuss the approach
2. **Break down large features** into smaller PRs
3. **Consider backwards compatibility**
4. **Plan for testing and documentation**
5. **Coordinate with maintainers**

## 📚 Resources

- [Project Architecture](docs/architecture.md)
- [API Documentation](docs/api-reference.md)
- [Healthcare Standards](docs/healthcare-standards.md)
- [Development Setup](docs/development.md)

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Project changelog
- Annual contributor recognition
- Conference presentations (with permission)

---

Thank you for contributing to FairClaimRCM! Together, we're making healthcare technology more transparent and fair.
