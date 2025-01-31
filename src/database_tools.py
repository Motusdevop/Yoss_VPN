from models import Tariff
from repository import TariffRepository


def create_price():
    list_tariffs = TariffRepository.get_all()

    if len(list_tariffs) == 0:
        one_month_tariff = Tariff(name="1 month", price=150)
        three_month_tariff = Tariff(name="3 month", price=300)

        TariffRepository.add(one_month_tariff)
        TariffRepository.add(three_month_tariff)
