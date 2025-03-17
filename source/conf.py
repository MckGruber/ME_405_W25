# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ME405 Romi Robot Term Project'
copyright = '2025, Joseph Balderama and Kelly Gruber'
author = 'Joseph Balderama & Kelly Gruber'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath('..'))

MOCK_MODULES = ['utime', 'pyb', 'machine']
sys.modules.update((mod_name, MagicMock()) for mod_name in MOCK_MODULES)

extensions = [
     'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages'
    ]

templates_path = ['_templates']
exclude_patterns = []
source_suffix = '.rst'
master_doc = 'index'

autodoc_mock_imports = ["pyb", "micropython"]

# make sure to include __init__
autoclass_content = 'both'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

pygments_style = 'sphinx'

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
}

html_static_path = ['_static']
