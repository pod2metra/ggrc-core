# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Main documentation builder script.

Use the following command to get usage message::

    $ python -m docbuilder --help

"""

import os
import shutil
from argparse import ArgumentParser

from sphinx.application import Sphinx

from docbuilder import builder

BASE_DIR = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')


def main():
    """Main documentation builder script."""
    parser = ArgumentParser(description="build GGRC documentation", )
    parser.add_argument(
        '-c',
        '--clean',
        action='store_true',
        default=False,
        help='clean cache before build',
        dest='clean',
    )
    parser.add_argument(
        '-s',
        '--strict',
        action='store_true',
        default=False,
        help='treat warnings as errors',
        dest='strict',
    )
    args = parser.parse_args()

    docs_src = os.path.join(DOCS_DIR, 'source')
    docs_build = os.path.join(DOCS_DIR, 'build')

    builder.build('API', os.path.join(docs_src, 'api'))

    if args.clean:
        shutil.rmtree(docs_build, ignore_errors=True)
    if not os.path.isdir(docs_build):
        os.mkdir(docs_build)

    sphinx = Sphinx(
        srcdir=docs_src,
        confdir=docs_src,
        outdir=os.path.join(docs_build, 'html'),
        doctreedir=os.path.join(docs_build, 'doctrees'),
        buildername='html',
        warningiserror=args.strict,
    )
    sphinx.build()
    return sphinx.statuscode


if __name__ == '__main__':
    main()
