# Contributing to OpenTransit

Thank you for your interest in contributing to OpenTransit! This guide explains how to get started.

## How to Contribute

1. **Fork** the repository and create a feature branch from `main`.
2. **Make your changes**, following the code style of the surrounding code.
3. **Add or update tests** for any changed behaviour.
4. **Run the test suite** and ensure all checks pass:
   ```bash
   pip install -r requirements-dev.txt
   pip audit            # security scan
   pytest               # unit and integration tests
   ruff check .         # linting
   ```
5. **Open a pull request** against `main` with a clear description of the change and the motivation behind it.

## Security Issues

Do **not** open a public issue for security vulnerabilities. Please follow the responsible disclosure process described in [SECURITY.md](SECURITY.md).

## Code of Conduct

Be respectful and constructive in all project interactions. Harassment or abusive behaviour will not be tolerated.
