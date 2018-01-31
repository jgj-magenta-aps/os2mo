#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Roles
-----------

This section describes how to interact with employee roles.

'''

import flask

from mora import lora
from mora.service.common import (create_organisationsfunktion_payload,
                                 ensure_bounds, inactivate_old_interval,
                                 update_payload)
from mora.service.mapping import (ORG_FUNK_GYLDIGHED_FIELD,
                                  ORG_FUNK_TYPE_FIELD, ORG_UNIT_FIELD,
                                  ROLE_FIELDS)

blueprint = flask.Blueprint('roles', __name__, static_url_path='',
                            url_prefix='/service')

ROLE_KEY = 'Rolle'

ROLE_TYPE = 'role_type'
ORG_UNIT = 'org_unit'
ORG = 'org'


def create_role(employee_uuid, req):
    # TODO: Validation

    org_unit_uuid = req.get(ORG_UNIT).get('uuid')
    org_uuid = req.get(ORG).get('uuid')
    role_type_uuid = req.get(ROLE_TYPE).get('uuid')
    valid_from = req.get('valid_from')
    valid_to = req.get('valid_to', 'infinity')

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, ROLE_KEY)

    role = create_organisationsfunktion_payload(
        funktionsnavn=ROLE_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=role_type_uuid,
    )

    lora.Connector().organisationfunktion.create(role)


def edit_role(employee_uuid, req):
    role_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=role_uuid)

    data = req.get('data')
    new_from = data.get('valid_from')
    new_to = data.get('valid_to', 'infinity')

    payload = dict()
    payload['note'] = 'Rediger rolle'

    overwrite = req.get('overwrite')
    if overwrite:
        # We are performing an update
        old_from = overwrite.get('valid_from')
        old_to = overwrite.get('valid_to')
        payload = inactivate_old_interval(
            old_from, old_to, new_from, new_to, payload,
            ('tilstande', 'organisationfunktiongyldighed')
        )

    update_fields = list()

    # Always update gyldighed
    update_fields.append((
        ORG_FUNK_GYLDIGHED_FIELD,
        {'gyldighed': "Aktiv"}
    ))

    if ROLE_TYPE in data.keys():
        update_fields.append((
            ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(ROLE_TYPE).get('uuid')},
        ))

    if ORG_UNIT in data.keys():
        update_fields.append((
            ORG_UNIT_FIELD,
            {'uuid': data.get(ORG_UNIT).get('uuid')},
        ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        ROLE_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    c.organisationfunktion.update(payload, role_uuid)