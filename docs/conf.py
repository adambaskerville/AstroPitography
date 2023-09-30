from __future__ import annotations

import importlib.metadata

project = "AstroPitography"
copyright = "{% now 'utc', '%Y' %}, Adam Baskerville"
author = "Adam Baskerville"
version = release = importlib.metadata.version("{{ cookiecutter.project_name | lower | replace('-', '_') | replace('.', '_') }}")

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "sphinx_material"

# A dictionary of options that influence the look and feel of the selected theme.
# These are theme-specific. Refer to your ``html_theme`` documentation for guidance.
html_theme_options = {
    "nav_title": "ASTROPITOGRAPHY",
    "repo_url": "https://bitbucket.org/exscientia/astropitography/",
    "repo_name": "astropitography",
    "repo_type": "bitbucket",
    "base_url": "http://docs.exsapps.com/astropitography/",
    "globaltoc_depth": 1,
    "globaltoc_collapse": True,
    "globaltoc_includehidden": True,
    "color_primary": "deep-orange",
    "color_accent": "orange",
    "html_minify": False,
    "html_prettify": True,
    "css_minify": True,
    "master_doc": False,
    "version_dropdown": False,
}

# The list of sidebars to include. Refer to your ``html_theme`` documentation for guidance on which are available.
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

# The title for the HTML documentation generated with Sphinx’s own templates. It is shown in your browser's tab.
html_title = "Docs | AstroPitography"

html_static_path = ["_static"]

# The logo for the docs: it is placed at the top of the sidebar - its width should not exceed 200 pixels
html_logo = "_static/images/logo.svg"

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
]

always_document_param_types = True
