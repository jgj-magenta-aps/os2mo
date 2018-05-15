#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import typing
from enum import Enum

import flask
import werkzeug.exceptions


class ErrorCodes(Enum):
    # Validation errors
    V_MISSING_REQUIRED_VALUE = 400, "Missing required value."
    V_INVALID_VALIDITY = 400, "Invalid validity."
    V_MISSING_START_DATE = 400, "Missing start date."
    V_END_BEFORE_START = 400, "End date is before start date."
    V_ORIGINAL_REQUIRED = 400, "Original required."
    V_NO_PERSON_FOR_CPR = 404, "No person found for given CPR number."
    V_CPR_NOT_VALID = 400, "Not a valid CPR number."
    V_ORG_UNIT_MOVE_TO_CHILD = \
        400, "Org unit cannot be moved to one of its own child units"
    V_TERMINATE_UNIT_WITH_CHILDREN_OR_ROLES = \
        400, "Cannot terminate unit with active children and roles."
    V_TERMINATE_UNIT_BEFORE_START_DATE = \
        400, "Cannot terminate org unit before its starting date."
    V_DATE_OUTSIDE_ORG_UNIT_RANGE = \
        400, "Date range exceeds validity range of associated org unit."
    V_DATE_OUTSIDE_EMPL_RANGE = \
        400, "Date range exceeds validity range of associated employee."
    V_CANNOT_MOVE_ROOT_ORG_UNIT = \
        400, "Moving the root org unit is not allowed"

    # Input errors
    E_ORG_UNIT_NOT_FOUND = 404, "Org unit not found."
    E_USER_NOT_FOUND = 404, "User not found."
    E_UNKNOWN_ROLE_TYPE = 400, "Unknown role type."
    E_INVALID_TYPE = 400, "Invalid type."
    E_INVALID_UUID = 400, "Invalid UUID."
    E_INVALID_URN = 400, "Invalid URN."
    E_ORIGINAL_ENTRY_NOT_FOUND = 400, "Original entry not found."
    E_INVALID_FUNCTION_TYPE = 400, "Invalid function type."
    E_NO_LOCAL_MUNICIPALITY = 400, "No local municipality found."
    E_SIZE_MUST_BE_POSITIVE = 400, "Size must be positive."

    # Misc
    E_INVALID_INPUT = 400, "Invalid input."
    E_UNAUTHORIZED = 401, "Unauthorized."
    E_CONNECTION_FAILED = 500, "Connection failed."
    E_NOT_FOUND = 404, "Not found."
    E_NO_SUCH_ENDPOINT = 404, "No such endpoint."
    E_UNKNOWN = 500, "Unknown Error."


class HTTPException(werkzeug.exceptions.HTTPException):
    key = ErrorCodes.E_UNKNOWN
    description = "Unknown error"
    code = 500

    def __init__(self,
                 error_key: typing.Optional[ErrorCodes]=None,
                 message: typing.Optional[str]=None,
                 **context) -> None:
        if error_key:
            self.key = error_key

        code, description = self.key.value

        if message:
            description = message
        self.description = description

        self.code = code
        self.context = context

        super().__init__(description)

    def get_headers(self, environ=None):
        return [('Content-Type', flask.current_app.config['JSONIFY_MIMETYPE'])]

    def get_body(self, environ=None):
        return flask.json.dumps(
            {
                'error': True,
                'description': self.description,
                'status': self.code,
                'error_key': self.key.name,

                **self.context,
            },
            indent=2,
        )
