#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora import lora
from tests import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_association(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "association",
                "org_unit": {'uuid': unitid},
                "job_function": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "association_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                'address_type': {
                    'example': '20304060',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                "address": {
                    'value': '33369696',
                },
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                    "to": "2017-12-02T00:00:00+01",
                },
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": userid
                    }
                ],
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": unitid
                    }
                ],
                "adresser": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        'urn': 'urn:magenta.dk:telefon:+4533369696',
                        'objekttype': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "6ee24785-ee9a-4502-81c2-"
                                             "7697009c9053 9d07123e-"
                                             "47ac-4a9a-88c8-da82e3a4bc9e "
                                             "Tilknytning",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            }
        }

        associations = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(associations), 1)
        associationid = associations[0]

        actual_association = c.organisationfunktion.get(associationid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(actual_association, expected)

        expected = [{
            'address': {
                'href': 'tel:+4533369696',
                'name': '3336 9696',
                'value': 'urn:magenta.dk:telefon:+4533369696',
            },
            'address_type': {
                'example': '20304060',
                'name': 'Telefonnummer',
                'scope': 'PHONE',
                'user_key': 'Telefon',
                'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
            },
            'association_type': {
                'example': None,
                'name': 'Medlem',
                'scope': None,
                'user_key': 'medl',
                'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
            },
            'job_function': None,
            'org_unit': {
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': unitid,
            },
            'person': {
                'name': 'Fedtmule',
                'uuid': userid,
            },
            'uuid': associationid,
            'validity': {
                'from': '2017-12-01T00:00:00+01:00',
                'to': '2017-12-02T00:00:00+01:00',
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/details/association'
            '?validity=future'.format(userid),
            expected,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association'
            '?validity=future'.format(unitid),
            expected,
        )

    def test_create_association_no_job_function(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "association",
                "org_unit": {'uuid': unitid},
                "association_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                'address_type': {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'Adresse',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                },
                "address": {
                    'value': '0a3f50a0-23c9-32b8-e044-0003ba298018',
                },
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                    "to": "2017-12-02T00:00:00+01",
                },
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
                "adresser": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "objekttype": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                        "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "6ee24785-ee9a-4502-81c2-"
                                             "7697009c9053 9d07123e-"
                                             "47ac-4a9a-88c8-da82e3a4bc9e "
                                             "Tilknytning",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            }
        }

        associations = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(associations), 1)
        associationid = associations[0]

        actual_association = c.organisationfunktion.get(associationid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(actual_association, expected)

        expected = [{
            'address': {
                'href': 'https://www.openstreetmap.org/'
                '?mlon=12.57924839&mlat=55.68113676&zoom=16',
                'name': 'Pilestræde 43, 3., 1112 København K',
                'value': '0a3f50a0-23c9-32b8-e044-0003ba298018',
            },
            'address_type': {
                'example': '<UUID>',
                'name': 'Adresse',
                'scope': 'DAR',
                'user_key': 'Adresse',
                'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
            },
            'association_type': {
                'example': None,
                'name': 'Medlem',
                'scope': None,
                'user_key': 'medl',
                'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
            },
            'job_function': None,
            'org_unit': {
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': unitid,
            },
            'person': {
                'name': 'Fedtmule',
                'uuid': userid,
            },
            'uuid': associationid,
            'validity': {
                'from': '2017-12-01T00:00:00+01:00',
                'to': '2017-12-02T00:00:00+01:00',
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/details/association'
            '?validity=future'.format(userid),
            expected,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association'
            '?validity=future'.format(unitid),
            expected,
        )

    def test_create_association_no_valid_to(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "association",
                "org_unit": {'uuid': unitid},
                "job_function": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "association_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                'address_type': {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'Adresse',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                },
                "address": {
                    'value': '0a3f50a0-23c9-32b8-e044-0003ba298018',
                },
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                },
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
                "adresser": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "objekttype": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                        "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "6ee24785-ee9a-4502-81c2-"
                                             "7697009c9053 9d07123e-"
                                             "47ac-4a9a-88c8-da82e3a4bc9e "
                                             "Tilknytning",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            }
        }

        associations = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(associations), 1)
        associationid = associations[0]

        actual_association = c.organisationfunktion.get(associationid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(actual_association, expected)

        expected = [{
            'address': {
                'href': 'https://www.openstreetmap.org/'
                '?mlon=12.57924839&mlat=55.68113676&zoom=16',
                'name': 'Pilestræde 43, 3., 1112 København K',
                'value': '0a3f50a0-23c9-32b8-e044-0003ba298018',
            },
            'address_type': {
                'example': '<UUID>',
                'name': 'Adresse',
                'scope': 'DAR',
                'user_key': 'Adresse',
                'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
            },
            'association_type': {
                'example': None,
                'name': 'Medlem',
                'scope': None,
                'user_key': 'medl',
                'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
            },
            'job_function': None,
            'org_unit': {
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            },
            'person': {
                'name': 'Fedtmule',
                'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
            },
            'uuid': associationid,
            'validity': {
                'from': '2017-12-01T00:00:00+01:00',
                'to': None,
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/details/association'
            '?validity=future'.format(userid),
            expected,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association'
            '?validity=future'.format(unitid),
            expected,
        )

    def test_edit_association_no_overwrite(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'

        req = [{
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "job_function": {
                    'uuid': "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                "association_type": {
                    'uuid': "bcd05828-cc10-48b1-bc48-2f0d204859b2"
                },
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_association = {
            "note": "Rediger tilknytning",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },

                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],

                # "adresser": [
                #     {
                #         "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                #         "virkning": {
                #             "from_included": True,
                #             "to_included": False,
                #             "from": "2017-01-01 00:00:00+01",
                #             "to": "2018-04-01 00:00:00+02"
                #         }
                #     },
                #     {
                #         "uuid": "47c51ade-cf1c-401c-afb7-a2f7d3455fcd",
                #         "virkning": {
                #             "from_included": True,
                #             "to_included": False,
                #             "from": "2018-04-01 00:00:00+02",
                #             "to": "infinity"
                #         }
                #     }
                # ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_association = c.organisationfunktion.get(association_uuid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(expected_association, actual_association)

        expected = [{
            'address': None,
            'address_type': None,
            'association_type': {
                'example': None,
                'name': 'Afdeling',
                'scope': None,
                'user_key': 'afd',
                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
            },
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
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            },
            'uuid': 'c2153d5d-4a2b-492d-a18c-c498f7bb6221',
            'validity': {
                'from': '2017-01-01T00:00:00+01:00',
                'to': '2018-04-01T00:00:00+02:00',
            },
        }]

        with self.subTest('present'):
            self.assertRequestResponse(
                '/service/e/{}/details/association'.format(userid),
                expected,
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/association'.format(unitid),
                expected,
            )

        with self.subTest('past'):
            self.assertRequestResponse(
                '/service/e/{}/details/association'
                '?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/association'
                '?validity=past'.format(unitid),
                [],
            )

        expected = [{
            'address': None,
            'address_type': None,
            'association_type': None,
            'job_function': None,
            'org_unit': {
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            },
            'person': {
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            },
            'uuid': association_uuid,
            'validity': {
                'from': '2018-04-01T00:00:00+02:00',
                'to': None,
            },
        }]

        with self.subTest('future'):
            self.assertRequestResponse(
                '/service/e/{}/details/association'
                '?validity=future'.format(userid),
                expected,
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/association'
                '?validity=future'.format(unitid),
                expected,
            )

    def test_edit_association_overwrite(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'

        req = [{
            "type": "association",
            "uuid": association_uuid,
            "original": {
                "validity": {
                    "from": "2017-01-01 00:00:00+01",
                    "to": None
                },
                "org_unit": {'uuid': unitid},
                "job_function": {
                    'uuid': "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"},
                "association_type": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "location": {'uuid': "0a3f50a0-23c9-32b8-e044-0003ba298018"}
            },
            "data": {
                "job_function": {
                    'uuid': "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                "association_type": {
                    'uuid': "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_association = {
            "note": "Rediger tilknytning",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                # "adresser": [
                #     {
                #         "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                #         "virkning": {
                #             "from_included": True,
                #             "to_included": False,
                #             "from": "2017-01-01 00:00:00+01",
                #             "to": "infinity"
                #         }
                #     }
                # ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_association = c.organisationfunktion.get(association_uuid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(expected_association, actual_association)

        self.assertRequestResponse(
            '/service/e/{}/details/association'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association'.format(unitid),
            [],
        )

        expected = [{
            'address': None,
            'address_type': None,
            'association_type': None,
            'job_function': None,
            'org_unit': {
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            },
            'person': {
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            },
            'uuid': association_uuid,
            'validity': {
                'from': '2018-04-01T00:00:00+02:00',
                'to': None,
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/details/association'
            '?validity=future'.format(userid),
            expected,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association'
            '?validity=future'.format(unitid),
            expected,
        )

    def test_edit_association_move(self):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        orig_unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        unitid = "b688513d-11f7-4efc-b679-ab082a2055d0"
        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'

        req = [{
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "org_unit": {'uuid': unitid},
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                    "to": "2019-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_association = {
            "note": "Rediger tilknytning",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        },
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2019-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "2019-04-01 00:00:00+02"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                # "adresser": [
                #     {
                #         "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                #         "virkning": {
                #             "from_included": True,
                #             "to_included": False,
                #             "from": "2017-01-01 00:00:00+01",
                #             "to": "infinity"
                #         }
                #     }
                # ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "2019-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2019-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_association = c.organisationfunktion.get(association_uuid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(expected_association, actual_association)

        expected = [{
            'address': None,
            'address_type': None,
            'association_type': {
                'example': None,
                'name': 'Afdeling',
                'scope': None,
                'user_key': 'afd',
                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
            },
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
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            },
            'person': {
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            },
            'uuid': association_uuid,
            'validity': {
                'from': '2017-01-01T00:00:00+01:00',
                'to': '2018-04-01T00:00:00+02:00',
            },
        }]

        # first, check pre-move
        self.assertRequestResponse(
            '/service/e/{}/details/association'.format(userid),
            expected,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association'.format(orig_unitid),
            expected,
        )

        # second, check post-move
        expected[0].update(validity={
            'from': '2019-04-01T00:00:00+02:00',
            'to': None,
        })

        self.assertRequestResponse(
            '/service/e/{}/details/association'
            '?at=2019-06-01'.format(userid),
            expected,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association'
            '?at=2019-06-01'.format(orig_unitid),
            expected,
        )

        # finally, check during the move
        expected[0].update(
            org_unit={
                'name': 'Samfundsvidenskabelige fakultet',
                'user_key': 'samf',
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
            },
            validity={
                'from': '2018-04-01T00:00:00+02:00',
                'to': '2019-04-01T00:00:00+02:00',
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/details/association?at=2018-06-01'.format(userid),
            expected,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/association?at=2018-06-01'.format(unitid),
            expected,
        )

    def test_edit_association_move_no_valid_to(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "b688513d-11f7-4efc-b679-ab082a2055d0"
        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'

        req = [{
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "org_unit": {'uuid': unitid},
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_association = {
            "note": "Rediger tilknytning",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        },
                    },
                    {
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                # "adresser": [
                #     {
                #         "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                #         "virkning": {
                #             "from_included": True,
                #             "to_included": False,
                #             "from": "2017-01-01 00:00:00+01",
                #             "to": "infinity"
                #         }
                #     }
                # ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_association = c.organisationfunktion.get(association_uuid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(expected_association, actual_association)

        expected = [{
            'address': None,
            'address_type': None,
            'association_type': {
                'example': None,
                'name': 'Afdeling',
                'scope': None,
                'user_key': 'afd',
                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
            },
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
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            },
            'uuid': association_uuid,
            'validity': {
                'from': '2017-01-01T00:00:00+01:00',
                'to': '2018-04-01T00:00:00+02:00',
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/details/association'.format(userid),
            expected,
        )

        expected[0].update(
            org_unit={
                'name': 'Samfundsvidenskabelige fakultet',
                'user_key': 'samf',
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
            },
            validity={
                'from': '2018-04-01T00:00:00+02:00',
                'to': None,
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/details/association'
            '?validity=future'.format(userid),
            expected,
        )

    def test_terminate_association(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "from": "2017-12-01T00:00:00+01"
            }
        }

        self.assertRequestResponse('/service/e/{}/terminate'.format(userid),
                                   userid, json=payload)

        expected = {
            "note": "Afslut medarbejder",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                # "adresser": [
                #     {
                #         "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                #         "virkning": {
                #             "from_included": True,
                #             "to_included": False,
                #             "from": "2017-01-01 00:00:00+01",
                #             "to": "infinity"
                #         }
                #     }
                # ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-12-01 00:00:00+01"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            },
        }

        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'

        actual_association = c.organisationfunktion.get(association_uuid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(actual_association, expected)


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class AddressTests(util.LoRATestCase):
    maxDiff = None

    @util.mock('aabogade.json', allow_mox=True)
    def test_edit_association_address(self, m):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'

        req = [{
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "address_type": {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                "address": {
                    "value": "user@example.com",
                },
                "validity": {
                    "from": "2017-01-01T00:00:00+01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected = [{
            'address': {
                'href': 'mailto:user@example.com',
                'name': 'user@example.com',
                'value': 'urn:mailto:user@example.com',
            },
            'address_type': {
                'example': 'test@example.com',
                'name': 'Emailadresse',
                'scope': 'EMAIL',
                'user_key': 'Email',
                'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            },
            'association_type': {
                'example': None,
                'name': 'Afdeling',
                'scope': None,
                'user_key': 'afd',
                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
            },
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
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            },
            'uuid': association_uuid,
            'validity': {
                'from': '2017-01-01T00:00:00+01:00',
                'to': None,
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/details/association'.format(userid),
            expected,
        )

        expected[0].update(
            validity={
                'from': '2017-01-01T00:00:00+01:00',
                'to': '2018-04-01T00:00:00+02:00',
            },
        )

        req = [{
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "address_type": {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'Adresse',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                },
                "address": {
                    "value": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
                "validity": {
                    "from": "2017-06-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected[0]['validity']['to'] = "2017-06-01T00:00:00+02:00"

        self.assertRequestResponse(
            '/service/e/{}/details/association'.format(userid),
            expected,
        )

        expected_association = {
            "note": "Rediger tilknytning",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "adresser": [
                    {
                        "urn": "urn:mailto:user@example.com",
                        "objekttype": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-06-01 00:00:00+02",
                        }
                    },
                    {
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-06-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-06-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-06-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_association = c.organisationfunktion.get(association_uuid)

        # drop lora-generated timestamps & users
        del actual_association['fratidspunkt'], actual_association[
            'tiltidspunkt'], actual_association[
            'brugerref']

        self.assertEqual(expected_association, actual_association)

        expected[0].update(
            address_type={
                'example': '<UUID>',
                'name': 'Adresse',
                'scope': 'DAR',
                'user_key': 'Adresse',
                'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
            },
            address={
                'href': 'https://www.openstreetmap.org/'
                '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                'name': 'Åbogade 15, 8200 Aarhus N',
                'value': '44c532e1-f617-4174-b144-d37ce9fda2bd',
            },
            validity={
                'from': '2017-06-01T00:00:00+02:00',
                'to': None,
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/details/association'
            '?validity=future'.format(userid),
            expected,
        )
