#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.

The three most important commands are ``build``, ``run`` and
``full-run``:

Use ``build`` for building the frontend sources. Then, use ``run`` to
serve the MORA webapp with reloading. This is particularly useful for
backend development.

Use ``full-run`` to run the entire stack, with webapp served with
reloading. The database is a one-off database, starting with the
same state as our TestCafé tests. This is primarily useful for
frontend development.

In addition, we have ``docs`` for building the documentation.

'''

import base64
import doctest
import json
import os
import random
import ssl
import subprocess
import sys
import threading
import traceback
import unittest
import warnings

import click
import flask
import requests
import urllib3
import werkzeug.serving

from .. import settings
from ..auth import tokens

basedir = os.path.dirname(os.path.dirname(__file__))
backenddir = os.path.dirname(basedir)
topdir = os.path.dirname(backenddir)
docsdir = os.path.join(topdir, 'docs')
frontenddir = os.path.join(topdir, 'frontend')

cli = flask.cli.FlaskGroup(help=__doc__)


class Exit(click.ClickException):
    '''A click exception for simply exiting the script'''

    def __init__(self, exit_code: int=1):
        self.exit_code = exit_code

    def show(self):
        pass


def get_yarn_cmd(cmd):
    with open(os.path.join(frontenddir, 'package.json')) as fp:
        info = json.load(fp)

    args = info['scripts'][cmd].split()

    if args[0] not in ('node', 'npm', 'yarn'):
        args[0] = os.path.join(frontenddir, 'node_modules', '.bin', args[0])

    return args


@cli.command()
@click.argument('target', required=False)
def build(target=None):
    'Build the frontend application.'

    subprocess.check_call(['yarn'], cwd=frontenddir)
    subprocess.check_call(get_yarn_cmd('build'), cwd=frontenddir)

    if target:
        subprocess.check_call(
            ['yarn', 'run'] + ([target] if target else []),
            cwd=frontenddir)


@cli.command()
@click.option('-b', '--open-browser', is_flag=True)
@click.argument('destdir', type=click.Path(), required=False)
def docs(open_browser, destdir):
    '''Build the documentation'''
    import webbrowser

    import sphinx.cmdline

    vuedoc_cmd = [
        os.path.join(frontenddir, 'node_modules', '.bin', 'vuedoc.md'),
        '--output', os.path.join(docsdir, 'vuedoc'),
    ] + [
        os.path.join(dirpath, file_name)
        for dirpath, dirs, file_names in
        os.walk(os.path.join(frontenddir, 'src'))
        for file_name in file_names
        if file_name.endswith('.vue')
    ]

    subprocess.check_call(vuedoc_cmd)

    if destdir:
        destdir = click.format_filename(destdir)
    else:
        destdir = os.path.join(topdir, 'docs', 'out', 'html')

    sphinx.cmdline.main(['-b', 'html', docsdir, destdir])

    if open_browser:
        webbrowser.get('default').open(click.format_filename(destdir))


@cli.command()
@click.option('--verbose', '-v', count=True,
              help='Show more output.')
@click.option('--quiet', '-q', is_flag=True,
              help='Suppress all output.')
@click.option('--failfast/--no-failfast', '-f',
              default=False, show_default=True,
              help='Stop at first failure.')
@click.option('--buffer/--no-buffer', '-b/-B',
              default=True, show_default=True,
              help='Toggle buffering of standard output during runs.')
@click.option('--minimox-dir', help='Location for a checkout of the '
              'minimox branch of LoRA.')
@click.option('--browser', help='Specify browser for Selenium tests, '
              'e.g. "Safari", "Firefox" or "Chrome".')
@click.option('--list', '-l', 'do_list', is_flag=True,
              help='List all available tests',)
@click.option('--xml-report', type=click.Path(),
              help='Write XML report to the given location',)
@click.option('--randomise', '--randomize', 'randomise', is_flag=True,
              help='Randomise execution order',)
@click.option('--keyword', '-k', 'keywords', multiple=True,
              help='Only run or list tests matching the given keyword',)
@click.argument('tests', nargs=-1)
def test(tests, quiet, verbose, minimox_dir, browser, do_list,
         keywords, xml_report, **kwargs):
    '''Test the application.'''
    sys.path.insert(0, backenddir)

    verbosity = 0 if quiet else verbose + 1

    if minimox_dir:
        os.environ['MINIMOX_DIR'] = minimox_dir

    if browser:
        os.environ['BROWSER'] = browser

    loader = unittest.TestLoader()

    # ensure that we can load the tests, whatever the $PWD
    sys.path.insert(0, backenddir)

    if tests:
        def as_module(tn):
            if os.path.isfile(tn) and tn.endswith('.py'):
                return '.'.join(
                    os.path.split(
                        os.path.splitext(
                            os.path.relpath(tn, backenddir)
                        )[0]
                    )
                )
            else:
                return tn

        suite = loader.loadTestsFromNames(map(as_module, tests))

    else:
        suite = loader.discover(
            start_dir=os.path.join(backenddir, 'tests'),
            top_level_dir=os.path.join(backenddir),
        )

        for module in sys.modules.values():
            module_file = getattr(module, '__file__', None)

            if module_file and module_file.startswith(basedir):
                suite.addTests(doctest.DocTestSuite(module))

    def expand_suite(suite):
        for member in suite:
            if isinstance(member, unittest.TestSuite):
                yield from expand_suite(member)
            else:
                yield member

    tests = list(expand_suite(suite))

    if keywords:
        tests = [
            case
            for k in keywords
            for case in tests
            if k.lower() in str(case).lower()
        ]

    if kwargs.pop('randomise'):
        random.SystemRandom().shuffle(tests)

    suite = unittest.TestSuite(tests)

    if do_list:
        for case in suite:
            if verbose:
                print(case)
            elif not quiet:
                print(case.id())

        return

    if xml_report:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(verbosity=verbosity,
                                         output=xml_report, **kwargs)

    else:
        runner = unittest.TextTestRunner(verbosity=verbosity, **kwargs)

    try:
        result = runner.run(suite)

    except Exception:
        if verbosity > 1:
            traceback.print_exc()
        raise

    if not result.wasSuccessful():
        raise Exit()


@cli.command('auth')
@click.option('--user', '-u',
              help="account user name",
              prompt='Enter user name')
@click.option('--password', '-p',
              help="account password")
@click.option('--raw', '-r', is_flag=True,
              help="don't pack and wrap the token")
@click.option('--verbose', '-v', is_flag=True,
              help="pretty-print the token")
@click.option('--insecure', '-k', is_flag=True,
              help="disable SSL/TLS security checks")
@click.option('--cert-only', '-c', is_flag=True,
              help="output embedded certificates in PEM form")
def auth_(**options):
    '''Test and extract authentication tokens from SAML IdP.'''
    if options['insecure']:
        warnings.simplefilter('ignore', urllib3.exceptions.HTTPWarning)
    else:
        warnings.simplefilter('error', urllib3.exceptions.HTTPWarning)

    if options['user'] and not options['password']:
        options['password'] = click.prompt(
            'Enter password for {}'.format(
                options['user'],
            ),
            hide_input=True,
            err=True,
        )

    try:
        # this is where the magic happens
        token = tokens.get_token(
            options['user'], options['password'],
            raw=options['raw'] or options['cert_only'],
            verbose=options['verbose'],
            insecure=options['insecure'],
        )
    except requests.exceptions.SSLError as e:
        msg = ('SSL request failed; you probably need to install the '
               'appropriate certificate authority, or use the correct '
               'host name.')
        print(msg, file=sys.stderr)
        print('error:', e, file=sys.stderr)

        raise click.Abort

    if not options['cert_only']:
        sys.stdout.write(token.decode())

    else:
        from lxml import etree

        for el in etree.fromstring(token).findall('.//{*}X509Certificate'):
            data = base64.standard_b64decode(el.text)

            sys.stdout.write(ssl.DER_cert_to_PEM_cert(data))


@cli.command()
def full_run(**kwargs):
    '''Runs a development server with a one-off LoRA.

    '''

    from unittest import mock

    import psycopg2

    from oio_rest import app as lora_app
    from oio_rest.utils import test_support
    import settings as lora_settings

    from mora import app
    from mora.importing import spreadsheets

    with \
            test_support.psql() as psql, \
            mock.patch('settings.LOG_AMQP_SERVER', None), \
            mock.patch('settings.DB_HOST', psql.dsn()['host'], create=True), \
            mock.patch('settings.DB_PORT', psql.dsn()['port'], create=True):
        test_support._initdb()

        lora_server = werkzeug.serving.make_server(
            'localhost', 0, lora_app.app,
            threaded=True,
        )

        lora_port = lora_server.socket.getsockname()[1]

        lora_thread = threading.Thread(
            target=lora_server.serve_forever,
            args=(),
            daemon=True,
        )

        lora_thread.start()

        with \
                mock.patch('oio_rest.db.pool',
                           psycopg2.pool.PersistentConnectionPool(
                               1, 100,
                               database=lora_settings.DATABASE,
                               user=psql.dsn()['user'],
                               password=psql.dsn().get('password'),
                               host=psql.dsn()['host'],
                               port=psql.dsn()['port'],
                           )), \
                mock.patch('mora.settings.LORA_URL',
                           'http://localhost:{}/'.format(lora_port)):
            print(' * LoRA running at {}'.format(settings.LORA_URL))

            spreadsheets.run(
                target=settings.LORA_URL.rstrip('/'),
                sheets=[
                    os.path.join(
                        backenddir,
                        'tests/fixtures/importing/BALLERUP.csv',
                    ),
                ],
                dry_run=False,
                verbose=False,
                jobs=1,
                failfast=False,
                include=None,
                check=False,
                exact=False,
            )

            mora_server = werkzeug.serving.make_server(
                'localhost', 0, app.create_app(),
                threaded=True,
            )

            mora_port = mora_server.socket.getsockname()[1]

            mora_thread = threading.Thread(
                target=mora_server.serve_forever,
                args=(),
                daemon=True,
            )

            mora_thread.start()

            with subprocess.Popen(
                get_yarn_cmd('dev'),
                cwd=frontenddir,
                env={
                    **os.environ,
                    'BASE_URL': 'http://localhost:{}'.format(mora_port),
                },
            ) as frontend:
                pass
