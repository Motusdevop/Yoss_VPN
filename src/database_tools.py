from models import Tariff
from repository import TariffRepository


def create_price():
    list_tariffs = TariffRepository.get_all()

    if len(list_tariffs) == 0:
        one_month_tariff = Tariff(name="1 month", price=200)
        three_month_tariff = Tariff(name="3 month", price=350)

        TariffRepository.add(one_month_tariff)
        TariffRepository.add(three_month_tariff)
    else:
        one_month_tariff = TariffRepository.get(1)
        three_month_tariff = TariffRepository.get(2)

        one_month_tariff.price = 200
        three_month_tariff.price = 350

        TariffRepository.update(one_month_tariff)
        TariffRepository.update(three_month_tariff)