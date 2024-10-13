
import json

class BotMode:
    __default = {
        "buy_action": True,
        "my_vpn_action": True
    }

    def __init__(self):
        self.buy_action = self.buy_action()
        self.my_vpn_action = self.my_vpn_action()
        self.status = f"buy_action: {self.buy_action} my_vpn_action: {self.my_vpn_action}"

    def buy_action(self):
        try:
            with open('bot_mode.json', 'r') as f:
                data = json.load(f)
            return data['buy_action']

        except FileNotFoundError:
            with open('bot_mode.json', 'w') as f:

                json.dump(BotMode.__default, f)
                return True

    def my_vpn_action(self):
        try:
            with open('bot_mode.json', 'r') as f:
                data = json.load(f)
            return data['my_vpn_action']

        except FileNotFoundError:

            with open('bot_mode.json', 'w') as f:
                json.dump(BotMode.__default, f)
                return True

    def set_buy_action(self, action: bool):
        self.buy_action = action

        data = BotMode.__default

        data['buy_action'] = self.buy_action

        with open('bot_mode.json', 'w') as f:
            json.dump(data, f)
        return self.buy_action

    def set_my_vpn_action(self, action: bool):
        self.my_vpn_action = action

        data = BotMode.__default

        data['my_vpn_action'] = self.my_vpn_action

        with open('bot_mode.json', 'w') as f:
            json.dump(data, f)
        return self.my_vpn_action




