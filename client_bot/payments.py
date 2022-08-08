import logging
from typing import Union

from client_bot.liqpay import LiqPay
import requests
from datetime import datetime

public_key = "i35726157240"
private_key = "IYKnnds4nCgejIuLaCXbfRr8LbwKrho6MaYPTqJ4"



class Payment:
    def __init__(self):
        self.liqpay = LiqPay(public_key, private_key)
        self.data_const = {
            "version": "3",
            "public_key": public_key,
        }

    def generate_new_url_for_pay(self, order_id, amount, text='') -> Union[str, None]:
        """
        Отримання від платіжної системи нового посилання на оплату
        :param order_id: унікальний id, який використовуються отримання інформації від платіжної системи по конкретній
                        оплаті
        :param amount: сума до сплати
        :param text: коментар, який бачить клієнт на сторінці оплати
        :return: url для оплати
        """
        # детальніше https://www.liqpay.ua/documentation/api/aquiring/checkout/doc
        # копіювання сталої частини даних для платежу
        data = {k: v for k, v in self.data_const.items()}
        # створення даних по поточному платежу
        data['action'] = "pay"
        data["amount"] = amount
        data["currency"] = "UAH"
        data["language"] = "uk"
        data["description"] = f"Оплата замовлення в боті. {text}"
        data["order_id"] = order_id
        data['server_url'] = 'http://[your_url]'
        data_to_sign = self.liqpay.data_to_sign(data)
        params = {'data': data_to_sign,
                  'signature': self.liqpay.cnb_signature(data)}
        res = None
        try:
            res = requests.post(url='https://www.liqpay.ua/api/3/checkout/', data=params)
            if res.status_code == 200:
                return res.url
            else:
                logging.warning(f"incorrect status code form response - {res.status_code}, must be 200, "
                                f"data- {data}, params - {params}")
                return
        except:
            logging.exception(f'error getting response from liqpay, '
                              f'res - {res}, data- {data}, params - {params}')

    def get_order_status_from_liqpay(self, order_id) -> Union[dict, bool]:
        data = {k: v for k, v in self.data_const.items()}
        data["action"] = "status"
        data["order_id"] = order_id
        res = self.liqpay.api("request", data)
        if res.get("action") == "pay":
            if res.get('public_key') == public_key:
                if res.get('status') == 'success':
                    print(res)
                    return True
        return False
