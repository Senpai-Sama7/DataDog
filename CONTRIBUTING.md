# Contributing to DataDog Platform

Thank you for your interest in contributing to the DataDog Universal Data Orchestration Platform! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to:

- Be respectful and considerate of others
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check the existing issues to see if the problem has already been reported
2. Collect relevant information (version, environment, steps to reproduce)

When creating a bug report, include:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Logs or error messages**

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
1. Check existing feature requests first
2. Provide a clear use case
3. Describe the expected behavior
4. Consider backward compatibility

### Pull Requests

#### Before Starting

1. **Open an issue** to discuss significant changes
2. **Fork the repository** and create a feature branch
3. **Follow coding standards** (see below)

#### Development Process

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DataDog.git
   cd DataDog
   git remote add upstream https://github.com/Senpai-Sama7/DataDog.git
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   pre-commit install
   ```

4. **Make your changes**:
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation as needed
   - Follow the style guide

5. **Run tests**:
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=datadog_platform
   
   # Run specific test
   pytest tests/unit/test_pipeline.py
   ```

6. **Format and lint**:
   ```bash
   # Format code
   black src/ tests/
   
   # Lint code
   ruff check src/ tests/
   
   # Type check
   mypy src/
   ```

7. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

#### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(connectors): add MongoDB connector

Implement MongoDB connector with async support.
Includes connection pooling and error handling.

Closes #123
```

```
fix(pipeline): resolve DAG cycle detection bug

Fix issue where cycles were not properly detected in
complex pipeline graphs.

Fixes #456
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters
- **Quotes**: Use double quotes for strings
- **Type hints**: Always include type hints
- **Docstrings**: Use Google style docstrings

### Code Quality

- **Type hints**: All functions must have type hints
- **Docstrings**: All public APIs must have docstrings
- **Tests**: New features must include tests
- **Coverage**: Maintain >80% test coverage

### Example Function

```python
def process_data(
    input_data: list[dict[str, Any]],
    transformation: Transformation,
    context: ExecutionContext
) -> list[dict[str, Any]]:
    """
    Process input data using the specified transformation.
    
    Args:
        input_data: List of data records to process
        transformation: Transformation to apply
        context: Execution context for tracking
        
    Returns:
        Processed data records
        
    Raises:
        ValueError: If input data is invalid
        TransformationError: If transformation fails
        
    Example:
        >>> data = [{"id": 1, "name": "Alice"}]
        >>> transform = Transformation(name="filter", ...)
        >>> result = process_data(data, transform, context)
    """
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    # Implementation here
    return processed_data
```

## Testing Guidelines

### Writing Tests

- Use `pytest` for all tests
- Follow the AAA pattern: Arrange, Act, Assert
- Use descriptive test names
- Test both success and failure cases
- Use fixtures for common setup

### Test Structure

```python
class TestPipeline:
    """Test cases for Pipeline class."""
    
    def test_pipeline_creation(self) -> None:
        """Test creating a basic pipeline."""
        # Arrange
        name = "test_pipeline"
        
        # Act
        pipeline = Pipeline(name=name)
        
        # Assert
        assert pipeline.name == name
        assert pipeline.pipeline_id is not None
    
    def test_invalid_pipeline_raises_error(self) -> None:
        """Test that invalid pipeline raises error."""
        with pytest.raises(ValueError):
            Pipeline(name="")
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows

## Documentation

### Code Documentation

- Use Google style docstrings
- Document all parameters and return values
- Include examples where helpful
- Keep docs up to date with code

### User Documentation

Update relevant documentation:
- `README.md` - For user-facing changes
- `docs/architecture.md` - For architectural changes
- `docs/api_reference.md` - For API changes
- Add examples in `examples/` directory

## Review Process

### Pull Request Review

All PRs are reviewed by maintainers:

1. **Automated checks** must pass (CI/CD)
2. **Code review** by at least one maintainer
3. **Testing** verification
4. **Documentation** review

### Review Criteria

- Code quality and style
- Test coverage
- Documentation completeness
- Backward compatibility
- Performance impact

### Addressing Feedback

- Respond to all comments
- Make requested changes
- Push updates to the same branch
- Request re-review when ready

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and discussions
- **Documentation**: https://datadog-platform.readthedocs.io

### Recognition

Contributors are recognized in:
- Release notes
- CONTRIBUTORS.md file
- GitHub insights

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or discussion if you have questions about contributing!
