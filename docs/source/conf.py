# Configuration file for the Sphinx documentation builder.
import sys
import os

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information


project = 'ExonViz'
copyright = '2023, LUMC'
author = 'Redmar van den Berg'

release = '0.2.17'
version = '.'.join(release.split('.')[0:2])

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']
master_doc = 'index'

autosummary_gneerate = True
# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
