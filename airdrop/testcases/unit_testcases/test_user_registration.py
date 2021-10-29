from unittest import TestCase
from airdrop.application.services.user_registration_services import UserRegistrationServices
from airdrop.infrastructure.models import AirdropWindow, UserRegistration
from airdrop.infrastructure.repositories.airdrop_repository import AirdropRepository
from airdrop.testcases.test_variables import AIRDROP
from datetime import datetime, timedelta
from airdrop.application.services.user_notification_service import UserNotificationService
from http import HTTPStatus


class UserRegistration(TestCase):
    def test_airdrop_registration(self):

        now = datetime.utcnow()
        one_month_later = now + timedelta(days=30)

        airdrop_repo = AirdropRepository()
        airdrop = airdrop_repo.register_airdrop(
            address='0x', org_name='SINGNET', token_name='AGIX', token_type='Contract', contract_address='0x', portal_link='https://beta.singularitynet.io', documentation_link='https://beta.singularitynet.io', github_link_for_contract='https://github.com/singnet', description='Long description')

        airdrop_repo.register_airdrop_window(airdrop_id=airdrop.id, airdrop_window_name='Airdrop Window 1', description='Long description', registration_required=True,
                                             registration_start_period=now, registration_end_period=one_month_later, snapshot_required=True, claim_start_period=now, claim_end_period=one_month_later)

        assert True

    def test_user_registration(self):
        inputs = {
            "airdrop_window_id": "1",
            "airdrop_id": "1",
            "address": "0x176133a958449C28930970989dB5fFFbEdd9F448",
            "signature": "958449C28930970989dB5fFFbEdd9F44989d33a958B5fF989dB5f33a958F",
        }
        status = UserRegistrationServices.register(inputs)
        self.assertEqual(status, 200)

    def test_attempt_reregistration(self):
        inputs = {
            "airdrop_window_id": "1",
            "airdrop_id": "1",
            "address": "0x176133a958449C28930970989dB5fFFbEdd9F448",
            "signature": "958449C28930970989dB5fFFbEdd9F44989d33a958B5fF989dB5f33a958F",
        }
        status = UserRegistrationServices.register(inputs)
        self.assertEqual(status, 400)

    def test_airdrop_window_user_eligibility(self):
        inputs = {
            "airdrop_window_id": "1",
            "airdrop_id": "1",
            "address": "0x176133a958449C28930970989dB5fFFbEdd9F448",
            "signature": "958449C28930970989dB5fFFbEdd9F44989d33a958B5fF989dB5f33a958F",
        }
        status = UserRegistrationServices.eligibility(inputs)
        self.assertEqual(status, 200)

    def test_airdrop_window_user_eligibility_with_invalid_info(self):
        inputs = {
            "airdrop_window_id": "100",
            "airdrop_id": "100",
            "address": "0x176133a958449C28930970989dB5fFFbEdd9F448",
            "signature": "958449C28930970989dB5fFFbEdd9F44989d33a958B5fF989dB5f33a958F",
        }
        status = UserRegistrationServices.eligibility(inputs)
        self.assertEqual(status, 400)

    def test_user_notification_subscription(self):
        payload = {
            "email": "email@provider.com",
        }
        status = UserNotificationService.subscribe_to_notifications(payload)
        self.assertEqual(status, HTTPStatus.OK.value)

    def test_user_notification_subscription_with_existing_email(self):
        payload = {
            "email": "email@provider.com",
        }
        status = UserNotificationService.subscribe_to_notifications(payload)
        self.assertEqual(status, HTTPStatus.BAD_REQUEST.value)
