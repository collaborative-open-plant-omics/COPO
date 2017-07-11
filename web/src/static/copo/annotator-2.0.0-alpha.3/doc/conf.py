# -*- coding: utf-8 -*-
#
# Annotator documentation build configuration file

import json
import os

# By default, we do not want to use the RTD theme
sphinx_rtd_theme = None

# If the docs are built on readthedocs, it will be used by default
if os.environ.get('READTHEDOCS') != 'True':
    try:
        import sphinx_rtd_theme
    except ImportError:
        # Now we know for sure we do not have it
        pass


# -- General configuration

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Annotator'
copyright = u'2014, The Annotator project contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = json.load(open('../package.json'))['version']
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# The default language to highlight source code in. This should be a valid
# Pygments lexer name.
highlight_language = 'javascript'


# -- Sphinx extension configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.extlinks',
    'sphinx.ext.todo',
    'sphinxcontrib.httpdomain',
]

# A dictionary of external sites, mapping unique short alias names to a base
# URL and a prefix.
extlinks = {
    'gh': ('https://github.com/openannotation/annotator/%s', ''),
    'issue': ('https://github.com/openannotation/annotator/issues/%s',
              'issue '),
}

# If this is True, todo and todolist produce output, else they produce nothing.
todo_include_todos = os.environ.get('SPHINX_TODOS') is not None


# -- Options for HTML output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme' if sphinx_rtd_theme else 'default'

# Add any paths that contain custom themes here, relative to this directory.
if sphinx_rtd_theme:
    html_theme_path = [
        sphinx_rtd_theme.get_html_theme_path()
    ]