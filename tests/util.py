#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import atexit
import contextlib
import functools
import json
import os
import select
import signal
import socket
import subprocess
import sys
import threading
import time
import unittest

import flask_testing
import requests_mock
import werkzeug.serving

from mora import lora, app, settings

TESTS_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(TESTS_DIR)
FIXTURE_DIR = os.path.join(TESTS_DIR, 'fixtures')
MOCKING_DIR = os.path.join(TESTS_DIR, 'mocking')


def jsonfile_to_dict(path):
    """
    Reads JSON from resources folder and converts to Python dictionary
    :param path: path to json resource
    :return: dictionary corresponding to the resource JSON
    """
    try:
        with open(os.path.join(BASE_DIR, path)) as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise ValueError('failed to decode ' + path)


def get_fixture(fixture_name):
    return jsonfile_to_dict(os.path.join(FIXTURE_DIR, fixture_name))


def get_mock_data(mock_name):
    return jsonfile_to_dict(os.path.join(MOCKING_DIR, mock_name))


def get_mock_text(mock_name, mode='r'):
    with open(os.path.join(MOCKING_DIR, mock_name), mode) as fp:
        return fp.read()


def get_unused_port():
    '''Obtain an unused port suitable for connecting to a server.

    Please note that due to not returning the allocated socket, this
    function is vulnerable to a race condition: in the time between
    call and port use, something else might acquire the port in
    question. However, this rarely happens in practice.

    '''
    with socket.socket() as sock:
        sock.bind(('', 0))
        return sock.getsockname()[1]


def load_fixture(path, fixture_name, uuid, *, verbose=False):
    '''Load a fixture, i.e. a JSON file with the 'fixtures' directory,
    into LoRA at the given path & UUID.

    '''
    if verbose:
        print('creating', path, uuid, file=sys.stderr)
    r = lora.create(path, get_fixture(fixture_name), uuid)
    return r


def load_sample_structures(*, verbose=False, minimal=False, check=False):
    '''Inject our test data into LoRA.

    '''
    fixtures = [(
        'organisation/organisation',
        'create_organisation_AU.json',
        '456362c4-0ee4-4e5e-a72c-751239745e62',
    )]

    units = {
        'root': '2874e1dc-85e6-4269-823a-e1125484dfd3',
    }

    classes = {
        'afdeling': '32547559-cfc1-4d97-94c6-70b192eff825',
    }

    facets = {
        'enhedstype': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280',
    }

    # TODO: add classifications, etc.

    functions = {
        'engagement': 'd000591f-8705-4324-897a-075e3623f37b',
    }

    users = {
        'andersand': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
        'fedtmule': '6ee24785-ee9a-4502-81c2-7697009c9053',
    }

    itsystems = {
        'ad': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
        'lora': '0872fb72-926d-4c5c-a063-ff800b8ee697',
    }

    if not minimal:
        units.update({
            'hum': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            'samf': 'b688513d-11f7-4efc-b679-ab082a2055d0',
            'fil': '85715fc7-925d-401b-822d-467eb4b163b6',
            'hist': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
            'frem': '04c78fc2-72d2-4d02-b55f-807af19eac48',
        })

        classes.update({
            'fakultet': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
            'institut': 'ca76a441-6226-404f-88a9-31e02e420e52',
        })

    for facetkey, facetid in facets.items():
        fixtures.append((
            'klassifikation/facet',
            'create_facet_{}.json'.format(facetkey),
            facetid,
        ))

    for classkey, classid in classes.items():
        fixtures.append((
            'klassifikation/klasse',
            'create_klasse_{}.json'.format(classkey),
            classid,
        ))

    for unitkey, unitid in units.items():
        fixtures.append((
            'organisation/organisationenhed',
            'create_organisationenhed_{}.json'.format(unitkey),
            unitid,
        ))

    for funckey, funcid in functions.items():
        fixtures.append((
            'organisation/organisationfunktion',
            'create_organisationfunktion_{}.json'.format(funckey),
            funcid,
        ))

    for userkey, userid in users.items():
        fixtures.append((
            'organisation/bruger',
            'create_bruger_{}.json'.format(userkey),
            userid,
        ))

    for itsystemkey, itsystemid in itsystems.items():
        fixtures.append((
            'organisation/itsystem',
            'create_itsystem_{}.json'.format(itsystemkey),
            itsystemid,
        ))

    for path, fixture_name, uuid in fixtures:
        if check:
            if lora.get(path, uuid):
                raise Exception('{} already exists at {}!'.format(
                    uuid, path,
                ))
        else:
            load_fixture(path, fixture_name, uuid, verbose=verbose)


@contextlib.contextmanager
def override_settings(**overrides):
    orig_settings = {k: getattr(settings, k) for k in overrides}
    settings.__dict__.update(overrides)
    yield
    settings.__dict__.update(orig_settings)


def override_lora_url(lora_url='http://mox/'):
    return override_settings(LORA_URL=lora_url)


def mock(name=None):
    '''Decorator for running a function under requests_mock, with the
    given mocking fixture loaded.
    '''

    def outer_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with requests_mock.mock() as mock:
                if name:
                    # inject the fixture; note that complete_qs is
                    # important: without it, a URL need only match *some*
                    # of the query parameters passed, and that's quite
                    # obnoxious if requests only differ by them
                    for url, value in get_mock_data(name).items():
                        mock.get(url, json=value, complete_qs=True)

                # pass the mocker object as the final parameter
                args = args + (mock,)

                with override_lora_url():
                    return func(*args, **kwargs)

        return wrapper

    return outer_wrapper


class TestCaseMixin(object):

    '''Base class for MO testcases w/o LoRA access.
    '''

    maxDiff = None

    def create_app(self):
        app.app.config['DEBUG'] = False
        app.app.config['TESTING'] = True
        app.app.config['LIVESERVER_PORT'] = 0
        app.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        return app.app

    @property
    def lora_url(self):
        return settings.LORA_URL

    def assertRequestResponse(self, path, expected, message=None, *,
                              status_code=None, drop_keys=(), **kwargs):
        '''Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        **kwargs is passed directly to the test client -- see the
        documentation for werkzeug.test.EnvironBuilder for details.

        One addition is that we support a 'json' argument that
        automatically posts the given JSON data.

        '''
        message = message or 'request {!r} failed'.format(path)

        r = self._perform_request(path, **kwargs)

        if status_code is None:
            self.assertLess(r.status_code, 300, message)
            self.assertGreaterEqual(r.status_code, 200, message)
        else:
            self.assertEqual(r.status_code, status_code, message)

        actual = r.json

        for k in drop_keys:
            try:
                actual.pop(k)
            except (IndexError, KeyError, TypeError):
                pass

        self.assertEqual(expected, actual, message)

    def assertRequestFails(self, path, code, message=None, **kwargs):
        '''Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        **kwargs is passed directly to the test client -- see the
        documentation for werkzeug.test.EnvironBuilder for details.

        One addition is that we support a 'json' argument that
        automatically posts the given JSON data.
        '''
        message = message or "request {!r} didn't fail properly".format(path)

        r = self._perform_request(path, **kwargs)

        self.assertEqual(r.status_code, code, message)

    def _perform_request(self, path, **kwargs):
        if 'json' in kwargs:
            # "In the face of ambiguity, refuse the temptation to guess."
            # ...so check that the arguments we override don't exist
            assert kwargs.keys().isdisjoint({'method', 'data', 'headers'})

            kwargs['method'] = 'POST'
            kwargs['data'] = json.dumps(kwargs.pop('json'), indent=2)
            kwargs['headers'] = {'Content-Type': 'application/json'}

        return self.client.open(path, **kwargs)


class LoRATestCaseMixin(TestCaseMixin):
    '''Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    '''

    def load_sample_structures(self, **kwargs):
        self.assertIsNone(self.minimox.poll(), 'LoRA is not running!')
        load_sample_structures(**kwargs)

    @unittest.skipUnless('MINIMOX_DIR' in os.environ, 'MINIMOX_DIR not set!')
    @classmethod
    def setUpClass(cls):
        port = get_unused_port()
        MINIMOX_DIR = os.getenv('MINIMOX_DIR')

        # Start a 'minimox' instance -- which is LoRA with the testing
        # tweaks in the 'minimox' branch. We use a separate process
        # since LoRA doesn't support Python 3, yet; the main downside
        # to this is that we have to take measures not to leak that
        # process.
        cls.minimox = subprocess.Popen(
            [os.path.join(MINIMOX_DIR, 'run-mox.py'), str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=MINIMOX_DIR,
        )

        cls._orig_lora = settings.LORA_URL
        settings.LORA_URL = 'http://localhost:{}/'.format(port)
        settings.SAML_IDP_TYPE = None

        # This is the first such measure: if the interpreter abruptly
        # exits for some reason, tell the subprocess to exit as well
        atexit.register(cls.minimox.send_signal, signal.SIGINT)

        # wait for the process to launch and print out its 'Listening...' line
        cls.minimox.stdout.readline()

    @classmethod
    def tearDownClass(cls):
        # first, we're cleaning up now, so clear the exit handler
        atexit.unregister(cls.minimox.send_signal)

        # second, terminate our child process
        cls.minimox.send_signal(signal.SIGINT)

        # read output from the server process
        print(cls.minimox.stdout.read())

        settings.LORA_URL = cls._orig_lora

    def setUp(self):
        super().setUp()

        self.assertIsNone(self.minimox.poll(), 'LoRA startup failed!')

    def tearDown(self):
        self.assertIsNone(self.minimox.poll(), 'LoRA startup failed!')

        # our test-runner enforces buffering of stdout, so we can
        # safely print out the process output; this ensures any
        # exceptions, etc. get reported to the user/test-runner
        while select.select((self.minimox.stdout,), (), (), 0)[0]:
            print(self.minimox.stdout.readline(), end='')

        # delete all objects in the test instance; this does 'leak'
        # information in that they continue to exist as registrations,
        # but it's faster than recreating the database fully
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        for t in map(c.__getattr__, c.scope_map):
            for objid in t(bvn='%'):
                t.delete(objid)

        while select.select((self.minimox.stdout,), (), (), 0)[0]:
            self.minimox.stdout.readline()

        super().tearDown()


class TestCase(TestCaseMixin, flask_testing.TestCase):
    pass


class LoRATestCase(LoRATestCaseMixin, flask_testing.TestCase):
    pass


class LiveLoRATestCase(LoRATestCaseMixin, flask_testing.LiveServerTestCase):
    #
    # The two methods below force the WSGI server to run in a thread
    # rather than a process. This enables easy coverage gathering as
    # output buffering.
    #
    def _spawn_live_server(self):
        self._server = werkzeug.serving.make_server(
            'localhost', self._port_value.value, self.app,
        )

        self._port_value.value = self._server.socket.getsockname()[1]

        self._thread = threading.Thread(
            target=self._server.serve_forever,
            args=(),
        )
        self._thread.start()

        # Copied from flask_testing

        # We must wait for the server to start listening, but give up
        # after a specified maximum timeout
        timeout = self.app.config.get('LIVESERVER_TIMEOUT', 5)
        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time)
            if elapsed_time > timeout:
                raise RuntimeError(
                    "Failed to start the server after %d seconds. " % timeout
                )

            if self._can_ping_server():
                break

    def _terminate_live_server(self):
        self._server.shutdown()
        self._thread.join()
