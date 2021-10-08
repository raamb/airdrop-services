from http import HTTPStatus
from jsonschema import validate, ValidationError
from datetime import datetime
from airdrop.infrastructure.repositories.airdrop_window_repository import AirdropWIndowRepository
from airdrop.infrastructure.repositories.user_repository import UserRepository
from airdrop.config import AirdropStrategy
from common.utils import verify_signature


class UserRegistrationServices:

    def airdrop_window_user_details(self, inputs):
        status = HTTPStatus.BAD_REQUEST

        try:
            schema = {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "airdrop_window_id": {"type": "string"},
                },
                "required": ["address", "airdrop_window_id"],
            }

            validate(instance=inputs, schema=schema)

            address = inputs["address"]
            airdrop_window_id = inputs["airdrop_window_id"]

            airdrop_window_user_details = UserRepository().airdrop_window_user_details(
                airdrop_window_id, address)

            if airdrop_window_user_details is None:
                raise Exception(
                    "Address is not registered for this airdrop window"
                )

            response = airdrop_window_user_details
            status = HTTPStatus.OK

        except ValidationError as e:
            response = e.message
        except BaseException as e:
            response = str(e)

        return status, response

    def eligibility(self, inputs):

        status = HTTPStatus.BAD_REQUEST

        try:
            schema = {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "signature": {"type": "string"},
                },
                "required": ["signature", "address", "airdrop_id", "airdrop_window_id"],
            }

            validate(instance=inputs, schema=schema)

            airdrop_id = inputs["airdrop_id"]
            airdrop_window_id = inputs["airdrop_window_id"]
            address = inputs["address"].lower()
            signature = inputs["signature"]

            airdrop_window = self.get_user_airdrop_window(
                airdrop_id, airdrop_window_id
            )

            if airdrop_window is None:
                raise Exception(
                    "Airdrop window is not accepting registration at this moment"
                )

            is_eligible_user = self.check_user_eligibility()

            if not is_eligible_user:
                raise Exception(
                    "Address is not eligible for this airdrop"
                )

            response = 'Address is eligible for Airdrop'
            status = HTTPStatus.OK

        except ValidationError as e:
            response = e.message
        except BaseException as e:
            response = str(e)

        return status, response

    def register(self, inputs):

        status = HTTPStatus.BAD_REQUEST

        try:
            schema = {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "signature": {"type": "string"},
                },
                "required": ["signature", "address", "airdrop_id", "airdrop_window_id"],
            }

            validate(instance=inputs, schema=schema)

            airdrop_id = inputs["airdrop_id"]
            airdrop_window_id = inputs["airdrop_window_id"]
            address = inputs["address"].lower()
            signature = inputs["signature"]

            verify_signature(airdrop_id, airdrop_window_id, address, signature)

            airdrop_window = self.get_user_airdrop_window(
                airdrop_id, airdrop_window_id
            )

            if airdrop_window is None:
                raise Exception(
                    "Airdrop window is not accepting registration at this moment"
                )

            is_eligible_user = self.check_user_eligibility()

            if not is_eligible_user:
                raise Exception(
                    "Address is not eligible for this airdrop"
                )

            is_registered_user = self.is_elgible_registered_user(
                airdrop_window_id, address)

            if is_registered_user is None:
                UserRepository().register_user(airdrop_window_id, address)

            response = HTTPStatus.OK.value
            status = HTTPStatus.OK
        except ValidationError as e:
            response = e.message
        except BaseException as e:
            response = str(e)

        return status, response

    def get_user_airdrop_window(self, airdrop_id, airdrop_window_id):
        now = datetime.utcnow()
        return AirdropWIndowRepository().is_open_airdrop_window(
            airdrop_id, airdrop_window_id, now
        )

    def is_elgible_registered_user(self, airdrop_window_id, address):
        return UserRepository().is_registered_user(
            airdrop_window_id, address
        )

    def check_user_eligibility(self):
        return True
        # TODO: Implement user eligibility check for AGIX airdrop