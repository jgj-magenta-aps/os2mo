#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora import lora
from mora import util as mora_util

from . import util


class Tests(util.LoRATestCase):
    def test_terminate_employee_in_the_past(self):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "to": "2000-12-01"
            }
        }

        # None of these should be activate at this point in time,
        # and should therefore remain unaffected by the termination request

        engagement_uuid = 'd000591f-8705-4324-897a-075e3623f37b'
        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'
        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'
        leave_uuid = 'b807628c-030c-4f5f-a438-de41c1f26ba5'
        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        def get_expected(id, is_manager=False):
            o = c.organisationfunktion.get(id)

            o.update(
                livscykluskode='Rettet',
                note='Afslut medarbejder',
            )

            if is_manager:
                del o['relationer']['tilknyttedebrugere'][0]['uuid']
            else:
                v = o['tilstande']['organisationfunktiongyldighed']
                v[0]['gyldighed'] = 'Inaktiv'

            return o

        expected_engagement = get_expected(engagement_uuid)
        expected_association = get_expected(association_uuid)
        expected_role = get_expected(role_uuid)
        expected_leave = get_expected(leave_uuid)
        expected_manager = get_expected(manager_uuid, True)

        self.assertRequestResponse('/service/e/{}/terminate'.format(userid),
                                   userid, json=payload)

        actual_engagement = c.organisationfunktion.get(engagement_uuid)
        actual_association = c.organisationfunktion.get(association_uuid)
        actual_role = c.organisationfunktion.get(role_uuid)
        actual_leave = c.organisationfunktion.get(leave_uuid)
        actual_manager = c.organisationfunktion.get(manager_uuid)

        with self.subTest('engagement'):
            self.assertRegistrationsEqual(expected_engagement,
                                          actual_engagement)

        with self.subTest('association'):
            self.assertRegistrationsEqual(expected_association,
                                          actual_association)

        with self.subTest('role'):
            self.assertRegistrationsEqual(expected_role,
                                          actual_role)

        with self.subTest('leave'):
            self.assertRegistrationsEqual(expected_leave,
                                          actual_leave)

        with self.subTest('manager'):
            self.assertRegistrationsEqual(expected_manager,
                                          actual_manager)
