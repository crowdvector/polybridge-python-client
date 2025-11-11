# Polybridge Python Client Documentation

This directory contains the Sphinx documentation for the Polybridge Python Client.

## Building Documentation Locally

### Prerequisites

Install the documentation dependencies:

```bash
# Using uv (recommended)
uv pip install -e ".[docs]"

# Or using pip
pip install -e ".[docs]"
```

### Build HTML Documentation

```bash
cd docs
make html
```

The generated HTML will be in `build/html/`. Open `build/html/index.html` in your browser to view.

### Other Build Formats

```bash
# Build PDF (requires LaTeX)
make latexpdf

# Build epub
make epub

# Clean build files
make clean
```

## Documentation Structure

- `source/conf.py` - Sphinx configuration
- `source/index.rst` - Main documentation page
- `source/installation.rst` - Installation instructions
- `source/quickstart.rst` - Quick start guide
- `source/user-guide.rst` - Comprehensive user guide
- `source/api-reference.rst` - Auto-generated API documentation
- `source/examples.rst` - Usage examples
- `source/changelog.rst` - Version history

## ReadTheDocs

The documentation is automatically built and hosted on ReadTheDocs at:
https://polybridge-python-client.readthedocs.io

Configuration is in `.readthedocs.yaml` in the project root.

## Adding New Documentation

1. Create a new `.rst` file in `source/`
2. Add it to the `toctree` in `source/index.rst`
3. Build locally to test: `make html`
4. Commit and push - ReadTheDocs will automatically rebuild

## Style Guide

- Use reStructuredText (`.rst`) for documentation pages
- Use NumPy-style docstrings in Python code
- Include code examples with proper syntax highlighting
- Keep line length under 100 characters for readability
