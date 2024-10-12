from datetime import datetime, timedelta

from models import Config, Subscription
from repository import ServerRepository, ConfigRepository, SubscriptionRepository
from tools import api


def create_config(username: str, user_id: int, server_id: int) -> Config:
    config_name = f'{username}_vpn'
    config = Config(name=config_name, user_id=user_id, server_id=server_id)

    server = ServerRepository.get(server_id)

    address = f'http://{server.address}:{server.port}'
    result = api.create_config(address, config_name)

    ServerRepository.update(server_id, count_of_configs=server.count_of_configs+1)

    config.file = result[config_name]
    config_id = ConfigRepository.add(config)

    return config
def create_subscription(user_id: int, config_id: int, days: int, test=False) -> int:

    expires_on = datetime.now() + timedelta(days=days)

    if test:
        expires_on = datetime.now() + timedelta(minutes=5)

    subscription = Subscription(user_id=user_id, config_id=config_id, expires_on=expires_on)

    subscription_id = SubscriptionRepository.add(subscription)

    return subscription_id