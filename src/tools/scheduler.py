import asyncio
import datetime

from aiogram.client.bot import Bot

from repository import (
    ConfigRepository,
    ServerRepository,
    SubscriptionRepository,
    UserRepository,
)
from tools import api


async def scheduler(bot: Bot):

    notications_list = []

    while True:
        time = datetime.datetime.now()

        subscriptions_list = SubscriptionRepository.get_all()
        for subscription in subscriptions_list:
            if subscription.expires_on <= time:
                config_id = subscription.config_id
                config = ConfigRepository.get(config_id)

                server = ServerRepository.get(config.server_id)
                ip_address = f"http://{server.address}:{server.port}"

                if not config.disabled and api.ping(ip_address):
                    if api.config_off(ip_address, config.name) == 200:
                        ConfigRepository.update(config_id, disabled=True)

                        user = UserRepository.get(subscription.user_id)
                        await bot.send_message(
                            user.chat_id,
                            f"ваша конфигурация на сервере {server.country} [{server.id}] отключена.",
                        )
                        await bot.send_message(
                            user.chat_id, f"Чтобы её включить, продлите подписку"
                        )

            elif (
                subscription.expires_on <= (time + datetime.timedelta(hours=24))
                and subscription.id not in notications_list
            ):
                user = UserRepository.get(subscription.user_id)

                config_id = subscription.config_id
                config = ConfigRepository.get(config_id)

                server = ServerRepository.get(config.server_id)

                await bot.send_message(
                    user.chat_id,
                    f"Через 24 часа, ваша конфигурация на сервере {server.country} [{server.id}] будет отключена.",
                )
                await bot.send_message(user.chat_id, f"Продлите подписку заранее")

                notications_list.append(subscription.id)

            servers = ServerRepository.get_all()

            for server in servers:
                ip_address = f"http://{server.address}:{server.port}"
                if api.ping(ip_address):
                    data = api.get_clients(ip_address)
                    print(data)
                    clients = data["clients"]
                    ServerRepository.update(server.id, count_of_configs=len(clients))

        await asyncio.sleep(120)
