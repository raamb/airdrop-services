from airdrop.infrastructure.repositories.base_repository import BaseRepository
from airdrop.infrastructure.models import AirdropWindow, UserRegistration, UserReward, UserNotifications
from airdrop.domain.factory.airdrop_factory import AirdropFactory
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


class UserRepository(BaseRepository):

    def subscribe_to_notifications(self, email):
        try:

            is_existing_email = self.session.query(UserNotifications.id).filter(
                UserNotifications.email == email).first()

            if is_existing_email is None:
                user_notifications = UserNotifications(email=email)
                self.add(user_notifications)
            else:
                raise Exception('Email already subscribed to notifications')

        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def check_rewards_awarded(self, airdrop_id, airdrop_window_id, address):
        try:
            query = text("select SUM(ur.rewards_awarded) AS 'total_rewards' FROM user_rewards ur, airdrop_window aw where ur.airdrop_window_id = aw.row_id and ur.address = :address and aw.airdrop_id = :airdrop_id and aw.claim_start_period <= current_timestamp and ur.airdrop_window_id not in (select airdrop_window_id from claim_history where address = :address and transaction_status in ('SUCCESS', 'PENDING'));")
            result = self.session.execute(
                query, {'address': address, 'airdrop_id': airdrop_id})
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

        balance_raw_data = result.fetchall()
        if len(balance_raw_data) > 0:
            balance_data = balance_raw_data[0]
            total_rewards = balance_data['total_rewards']
            return True, str(total_rewards)
        else:
            return False, 0

    def airdrop_window_user_details(self, airdrop_window_id, address):
        user_data = (
            self.session.query(UserRegistration)
            .join(
                AirdropWindow,
                AirdropWindow.id == UserRegistration.airdrop_window_id,
            )
            .filter(UserRegistration.airdrop_window_id == airdrop_window_id)
            .filter(UserRegistration.address == address)
            .filter(UserRegistration.registered_at != None)
            .first()
        )

        user_details = None

        if user_data is not None:
            user_details = AirdropFactory.convert_airdrop_window_user_model_to_entity_model(
                user_data)

        return user_details

    def get_reject_reason(self, airdrop_window_id, address):
        registration = (
            self.session.query(UserRegistration.reject_reason)
            .filter(UserRegistration.airdrop_window_id == airdrop_window_id)
            .filter(UserRegistration.address == address)
            .first()
        )

        return registration.reject_reason if registration is not None else None

    def is_registered_user(self, airdrop_window_id, address):
        is_registered_user = (
            self.session.query(UserRegistration.id)
            .filter(UserRegistration.airdrop_window_id == airdrop_window_id)
            .filter(UserRegistration.address == address)
            .filter(UserRegistration.registered_at != None)
            .first()
        )

        if is_registered_user is None:
            return False
        else:
            return True

    def register_user(self, airdrop_window_id, address):
        user = UserRegistration(
            address=address, airdrop_window_id=airdrop_window_id, registered_at=datetime.utcnow())
        self.add(user)
