# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "astrophotography"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx_toolbox.confval",
    "sphinx_togglebutton",
    "myst_nb",
    "sphinx_design",
    "sphinx_sitemap",
    "sphinx_inline_tabs",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_baseurl = "https://adambaskerville.github.io/astropitography"
html_favicon = "_static/AstroPitographyLogoSmall.png"

html_title = "AstroPhotography"
html_logo = "_static/AstroPitographyLogoSmall.png"

html_theme_options = {
    "logo": {
        "image_dark": "_static/AstroPitographyLogoSmall.png",
        "image_light": "_static/AstroPitographyLogoSmall.png",
    },
    "repository_url": "https://github.com/adambaskerville/AstroPitography",
    "use_repository_button": True,
    "use_sidenotes": True,
    "show_nav_level": 0,
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/astropitography/",
            "icon": "https://img.shields.io/pypi/v/astropitography",
            "type": "url",
        },
    ],
}
