from requests import get, post, delete
from urllib.parse import urlencode

from config import settings

auth = ('bot', settings.server_password.get_secret_value())

def create_config(ip_address: str, config_name: str) -> dict:
    data = {'config_name': config_name}
    res = post(ip_address + '/api/vpn/add', json=data, auth=auth)
    return res.json()


def get_clients(ip_address: str) -> dict:
    res = get(ip_address + '/api/vpn/list', auth=auth)
    return res.json()


def config_on(ip_address: str, config_name: str) -> int:
    res = post(ip_address + f'/api/vpn/on/{config_name}', auth=auth)
    return res.status_code


def config_off(ip_address: str, config_name: str) -> int:
    res = post(ip_address + f'/api/vpn/off/{config_name}', auth=auth)
    return res.status_code


def delete_config(ip_address: str, config_name: str) -> int:
    res = delete(ip_address + f'/api/vpn/delete/{config_name}', auth=auth)
    return res.status_code

def ping(ip_address: str) -> bool:
    res = get(ip_address + f'/')

    if res.json()['message'] == 'Hello World':
        return True
    else:
        return False


def generate_qr(config: str) -> str:
    data = {'data': config}
    text = urlencode(data)
    return f'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={text}'


if __name__ == '__main__':
    ip_address = 'http://138.124.30.198:8000'
    config_name = 'test_config'
    print(create_config(ip_address, config_name)[config_name])
    print(delete_config(ip_address, config_name))
