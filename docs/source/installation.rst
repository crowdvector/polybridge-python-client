Installation
============

Requirements
------------

* Python 3.8+
* requests >= 2.31.0
* pandas >= 2.0.0

Install from Source
-------------------

Clone the repository and install the package:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/crowdvector/polybridge-python-client.git
   cd polybridge-python-client

   # Install the package
   pip install .

Development Installation
------------------------

For development work, install in editable mode with optional dependencies:

Using uv (recommended)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   uv venv

   # Activate it
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install in development mode with all optional dependencies
   uv pip install -e ".[dev,notebooks]"

Using standard Python tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   python -m venv .venv

   # Activate it
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install in development mode
   pip install -e ".[dev,notebooks]"

Optional Dependencies
---------------------

The package supports the following optional dependency groups:

* ``dev``: Development tools (pytest, black, ruff, mypy)
* ``notebooks``: Jupyter notebook support (jupyter, notebook, ipykernel, matplotlib)

Install specific groups:

.. code-block:: bash

   pip install -e ".[dev]"          # Just dev tools
   pip install -e ".[notebooks]"    # Just notebooks
   pip install -e ".[dev,notebooks]" # Both

Verify Installation
-------------------

Verify the installation by importing the package:

.. code-block:: python

   from polybridge import PolybridgeClient
   print("Polybridge client installed successfully!")
