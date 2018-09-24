#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import sys
import traceback
import typing
from enum import Enum

import flask
import werkzeug.exceptions


class ErrorCodes(Enum):
    '''This enumeration describes the possible errors codes returned by
    the application. Each item in the enumeration consists of three
    values:

    * A unique string identifying the code.
    * An integer identifying the HTTP status code returned for the
      error — see :rfc:`2616#section-10`.
    * An human-readable string describing the circumstances of the
      error.

    The special code :py:attr:`mora.exceptions.ErrorCodes.E_UNKNOWN`
    means that an unknown, internal error occurred within the
    application. This is most likely a bug.

    '''

    @property
    def description(self):
        return self.value[1]

    @property
    def code(self):
        return self.value[0]

    # Validation errors
    V_MISSING_REQUIRED_VALUE = 400, "Missing required value."
    V_INVALID_VALIDITY = 400, "Invalid validity."
    V_MISSING_START_DATE = 400, "Missing start date."
    V_END_BEFORE_START = 400, "End date is before start date."
    V_ORIGINAL_REQUIRED = 400, "Original required."
    V_EXISTING_CPR = 409, "Person with CPR number already exists."
    V_NO_PERSON_FOR_CPR = 404, "No person found for given CPR number."
    V_CPR_NOT_VALID = 400, "Not a valid CPR number."
    V_ORG_UNIT_MOVE_TO_CHILD = \
        400, "Org unit cannot be moved to one of its own child units"
    V_TERMINATE_UNIT_WITH_CHILDREN_OR_ROLES = \
        400, "Cannot terminate unit with active children and roles."
    V_DATE_OUTSIDE_ORG_UNIT_RANGE = \
        400, "Date range exceeds validity range of associated org unit."
    V_DATE_OUTSIDE_EMPL_RANGE = \
        400, "Date range exceeds validity range of associated employee."
    V_CANNOT_MOVE_ROOT_ORG_UNIT = \
        400, "Moving the root org unit is not allowed"
    V_CANNOT_MOVE_UNIT_TO_ROOT_LEVEL = \
        400, "Moving an org unit to the root level is not allowed"
    V_MORE_THAN_ONE_ASSOCIATION = \
        400, "The employee already has an active association with the given " \
             "org unit."
    V_NO_ACTIVE_ENGAGEMENT = \
        400, "Employee must have an active engagement."
    V_UNIT_OUTSIDE_ORG = \
        400, "Unit belongs to an organisation different from the current one."
    V_PARENT_NOT_FOUND = \
        404, "Corresponding parent unit or organisation not found."
    V_DUPLICATED_RESPONSIBILITY = \
        400, "Manager has the same responsibility more than once."

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
    E_FORBIDDEN = 403, "Forbidden."
    E_CONNECTION_FAILED = 500, "Connection failed."
    E_NOT_FOUND = 404, "Not found."
    E_NO_SUCH_ENDPOINT = 404, "No such endpoint."
    E_UNKNOWN = 500, "Unknown Error."


class HTTPException(werkzeug.exceptions.HTTPException):
    key = ErrorCodes.E_UNKNOWN

    @property
    def code(self):
        return self.key.code

    def __init__(self,
                 error_key: typing.Optional[ErrorCodes]=None,
                 message: typing.Optional[str]=None,
                 *,
                 cause=None,
                 **extras) -> None:

        if error_key is not None:
            self.key = error_key

        body = {
            'error': True,
            'description': message or self.key.description,
            'status': self.key.code,
            'error_key': self.key.name,
            **extras,
        }

        # this aids debugging
        if flask.current_app.debug:
            if cause is None:
                self.__cause__ or sys.exc_info()[1]

            if isinstance(cause, Exception):
                body.update(
                    exception=str(cause),
                    context=traceback.format_exc().splitlines(),
                )
            elif cause:
                body['context'] = cause

        super().__init__(body['description'])

        try:
            self.body = body
            self.response = flask.jsonify(body)
            self.response.status_code = self.key.code
        except RuntimeError:
            pass
