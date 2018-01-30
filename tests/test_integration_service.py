#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime

import freezegun

from mora import lora

from . import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_organisation(self):
        with self.subTest('empty'):
            self.assertRequestResponse('/service/o/', [])

            self.assertRequestFails(
                '/service/o/00000000-0000-0000-0000-000000000000/',
                404,
            )

        self.load_sample_structures(minimal=True)

        org_list = [
            {
                'name': 'Aarhus Universitet',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'user_key': 'AU',
            }
        ]

        org_only = {
            'name': 'Aarhus Universitet',
            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
            'user_key': 'AU',
            'unit_count': 1,
            'person_count': 2,
            'employment_count': 2,
            'child_count': 1,
        }

        self.assertRequestResponse('/service/o/', org_list)

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/',
            org_only,
        )

        with self.subTest('time machine'):
            old_time = datetime.date(2015, 1, 1).isoformat()
            new_time = datetime.date(2017, 1, 1).isoformat()

            with freezegun.freeze_time(new_time, tz_offset=1):
                self.assertRequestResponse(
                    '/service/o/?at=' + old_time, [],
                )

                self.assertRequestFails(
                    '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/?at=' +
                    old_time,
                    404,
                )

            with freezegun.freeze_time(old_time, tz_offset=1):
                self.assertRequestResponse(
                    '/service/o/?at=' + new_time, org_list,
                )

                self.assertRequestResponse(
                    '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/?at=' +
                    new_time,
                    org_only,
                )

        self.load_sample_structures()
        org_only['unit_count'] = 6

        self.assertRequestResponse(
            '/service/o/',
            org_list,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/',
            org_only,
        )

        with self.subTest('deleted'):
            lora.delete('organisation/organisationenhed',
                        '2874e1dc-85e6-4269-823a-e1125484dfd3')

            self.assertRequestResponse('/service/o/', [])

            # we don't care much about this case; why would you query
            # an unlisted organisation? let's test it regardless...
            org_only['unit_count'] = 5
            org_only['child_count'] = 0
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/', org_only,
            )

    def test_children(self):
        self.load_sample_structures(minimal=True)

        with self.subTest('invalid'):
            self.assertRequestFails(
                '/service/o/00000000-0000-0000-0000-000000000000/children',
                404,
            )

            self.assertRequestFails(
                '/service/ou/00000000-0000-0000-0000-000000000000/children',
                404,
            )

        with self.subTest('resolving a unit as an org, and vice versa'):
            self.assertRequestFails(
                '/service/o/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
                404,
            )
            self.assertRequestFails(
                '/service/ou/456362c4-0ee4-4e5e-a72c-751239745e62/children',
                404,
            )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/children',
            [
                {
                    'child_count': 0,
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
            [],
        )

        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/children',
            [
                {
                    'child_count': 2,
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
            [
                {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "child_count": 2,
                },
                {
                    "name": "Samfundsvidenskabelige fakultet",
                    "user_key": "samf",
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "child_count": 0,
                }
            ],
        )

    def test_orgunit_search(self):
        self.load_sample_structures()

        result_list = [
            {
                'user_key': 'frem',
                'name': 'Afdeling for Samtidshistorik',
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
            },
            {
                'user_key': 'root',
                'name': 'Overordnet Enhed',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
            {
                'user_key': 'fil',
                'name': 'Filosofisk Institut',
                'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
            },
            {
                'user_key': 'hum',
                'name': 'Humanistisk fakultet',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            },
            {
                'user_key': 'samf',
                'name': 'Samfundsvidenskabelige fakultet',
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
            },
            {
                'user_key': 'hist',
                'name': 'Historisk Institut',
                'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
            },
        ]

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/',
            result_list,
        )

        with self.subTest('list with a limit'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=2',
                [
                    {
                        'user_key': 'hum',
                        'name': 'Humanistisk fakultet',
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    },
                    {
                        'user_key': 'hist',
                        'name': 'Historisk Institut',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                ],
            )

        with self.subTest('list with a limit and a start'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=1',
                result_list[1:4],
            )

        with self.subTest('paging'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3',
                [
                    {
                        'user_key': 'root',
                        'name': 'Overordnet Enhed',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    },
                    {
                        'user_key': 'hum',
                        'name': 'Humanistisk fakultet',
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    },
                    {
                        'user_key': 'hist',
                        'name': 'Historisk Institut',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=3',
                [
                    {
                        'user_key': 'frem',
                        'name': 'Afdeling for Samtidshistorik',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    },
                    {
                        'user_key': 'fil',
                        'name': 'Filosofisk Institut',
                        'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    },
                    {
                        'user_key': 'samf',
                        'name': 'Samfundsvidenskabelige fakultet',
                        'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    },
                ],
            )

        with self.subTest('searching'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?query=frem',
                [
                    {
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'name': 'Afdeling for Samtidshistorik',
                        'user_key': 'frem',
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?query=over',
                [
                    {
                        'name': 'Overordnet Enhed',
                        'user_key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    }
                ],
            )

    def test_orgunit(self):
        self.load_sample_structures(minimal=True)

        with self.subTest('invalid'):
            self.assertRequestFails(
                '/service/ou/00000000-0000-0000-0000-000000000000/',
                404,
            )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                'child_count': 0,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/tree',
            {
                'children': [],
                'parent': None,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                'child_count': 2,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/tree',
            {
                'children': [
                    {
                        'child_count': 2,
                        'name': 'Humanistisk fakultet',
                        'user_key': 'hum',
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    },
                    {
                        'child_count': 0,
                        'name': 'Samfundsvidenskabelige fakultet',
                        'user_key': 'samf',
                        'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    },
                ],
                'parent': None,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/tree',
            {
                'children': [
                    {
                        'child_count': 0,
                        'name': 'Filosofisk Institut',
                        'user_key': 'fil',
                        'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    },
                    {
                        'child_count': 1,
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                ],
                'parent': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            },
        )

    def test_employee(self):
        with self.subTest('empty'):
            self.assertRequestResponse(
                '/service/o/00000000-0000-0000-0000-000000000000/e/',
                [],
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
                [],
            )

        self.load_sample_structures(minimal=True)

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/e/',
            [],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
            [
                {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                {
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/',
            {
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                'cpr_no': '1111111111',
            },
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/',
            {
                'name': 'Fedtmule',
                'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                'cpr_no': '2222222222',
            },
        )

        with freezegun.freeze_time('1950-01-01'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
                [],
            )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=1950-01-01T00%3A00%3A00%2B01%3A00',
            [],
        )

        util.load_fixture('organisation/bruger',
                          'create_bruger_andersine.json',
                          'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24')

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
            [
                {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                {
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                {
                    'name': 'Andersine And',
                    'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?limit=1',
            [
                {
                    'name': 'Andersine And',
                    'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?limit=1&start=1',
            [
                {
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=2005-01-01T00%3A00%3A00%2B01%3A00',
            [
                {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                {
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=Anders',
            [
                {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                {
                    'name': 'Andersine And',
                    'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=2005-01-01T00%3A00%3A00%2B01%3A00&query=Anders',
            [
                {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
            ],
        )

    def test_engagement(self):
        self.load_sample_structures()

        func = [
            {
                'job_function': {
                    'example': None,
                    'name': 'Fakultet',
                    'scope': None,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'cpr_no': '1111111111',
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                'valid_from': '2017-01-01T00:00:00+01:00',
                'valid_to': None,
            },
        ]

        with self.subTest('user'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement',
                func,
            )

        with self.subTest('past'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement?validity=past',
                [],
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement?validity=future',
                [],
            )

            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement?at=2016-01-01&validity=future',
                func,
            )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/engagement',
            func,
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
            '/details/engagement',
            [],
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000'
            '/details/engagement',
            [],
        )

    def test_facet(self):
        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/',
            [],
        )

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/address/',
            [],
        )

        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/f/kaflaflibob/',
            404,
        )

        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/ou/',
            [],
        )

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/address/',
            [],
        )

        self.assertRequestFails(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/kaflaflibob/',
            404,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/',
            [{'name': 'address',
              'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
              '/f/address/',
              'user_key': 'Adressetype',
              'uuid': 'e337bab4-635f-49ce-aa31-b44047a43aa1'},
             {'name': 'ou',
              'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
              '/f/ou/',
              'user_key': 'Enhedstype',
              'uuid': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280'}],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/ou/',
            [{'example': None,
              'name': 'Afdeling',
              'scope': None,
              'user_key': 'afd',
              'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'},
             {'example': None,
              'name': 'Fakultet',
              'scope': None,
              'user_key': 'fak',
              'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'},
             {'example': None,
              'name': 'Institut',
              'scope': None,
              'user_key': 'inst',
              'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'}],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address/',
            [{'example': '<UUID>',
              'name': 'Adresse',
              'scope': 'DAR',
              'user_key': 'Adresse',
              'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed'},
             {'example': 'EAN',
              'name': 'EAN',
              'scope': 'INTEGER',
              'user_key': 'EAN',
              'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2'},
             {'example': 'test@example.com',
              'name': 'Emailadresse',
              'scope': 'EMAIL',
              'user_key': 'Email',
              'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0'},
             {'example': '20304060',
              'name': 'Telefonnummer',
              'scope': 'PHONE',
              'user_key': 'Telefon',
              'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec'}],
        )

    def test_itsystem(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/it/',
            [

                {
                    'type': None,
                    'user_key': 'LoRa',
                    'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                    'name': 'Lokal Rammearkitektur',
                },
                {
                    'type': None,
                    'user_key': 'AD',
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    'name': 'Active Directory',
                }
            ],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it',
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              'valid_from': '2002-02-14T00:00:00+01:00',
              'valid_to': None},
             {'name': 'Lokal Rammearkitektur',
              'user_name': 'Fedtmule',
              'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
              'valid_from': '2016-01-01T00:00:00+01:00',
              'valid_to': '2018-01-01T00:00:00+01:00'}],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?validity=past',
            [],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?validity=future',
            [],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?at=2018-06-01',
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              'valid_from': '2002-02-14T00:00:00+01:00',
              'valid_to': None}],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?at=2018-06-01&validity=past',
            [{'name': 'Lokal Rammearkitektur',
              'user_name': 'Fedtmule',
              'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
              'valid_from': '2016-01-01T00:00:00+01:00',
              'valid_to': '2018-01-01T00:00:00+01:00'}],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?at=2018-06-01&validity=future',
            [],
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/it',
            [],
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/details/it',
            [],
        )
