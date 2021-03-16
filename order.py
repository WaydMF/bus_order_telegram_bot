from bs4 import BeautifulSoup as bs4
import datetime
import json
import requests


class Order(object):
    city_from = None
    city_to = None
    date = None

    city_mapping = {"д. Переходы": 16,"71 км": 11, "выезд из д. Крево": 19, "г. Сморгонь": 22,
                    "д. Байдаки": 6, "д. Белькишки": 25, "д. Василевичи": 48, "д. Гаути": 42,
                    "д. Дайлидки": 38, "д. Дегенево": 27, "д. Изобелино": 36, "д. Крево  почта": 20,
                    "д. Крево 2": 64, "д. Кунава": 51, "д. Куцевичи": 30, "д. Лубянка": 43,
                    "д. Мацканы": 37, "д. Медрики": 40, "д. Милейково": 17, "д. Михалкони": 28,
                    "д. Михалова": 63, "д. Новоселки": 29, "д. Новоспаск": 53, "д. Ореховка": 46,
                    "д. Осиновщизна": 45, "д. Подберезь": 33, "д. Раковцы": 18, "д. Светоч": 50,
                    "д. Свиридовичи": 49, "д. Солы": 41, "д. Сутьково": 52, "д. Тракели": 39,
                    "д.Богуши": 55, "д.Гарани": 7, "д.Крево 3": 21, "д.Лавский Брод": 15,
                    "д.Селец": 54, "Лесная сказка": 8, "Минск": 5, "Остр. кольцо": 35,
                    "Островец": 23, "Ошмяны": 24, "пов. на д. Боруны": 31, "пов. на д. Трайги": 26,
                    "пов. на Сморг. погран. группа": 44, "трасса М6 Воложинский пост": 65,
                    "трасса М7 д. Дайнова Большая": 67, "трасса М7 пов. на ст. Воложин": 66}


    def __init__(self, user_language):
        self.user_language = user_language

    def _get_info_http(self):

        city_from = self.city_mapping.get(self.city_from)
        city_to = self.city_mapping.get(self.city_to)
        date = self.date
        request_url = "http://xn--90aiim0b.xn--80aa3agllaqi6bg.xn--90ais/schedules"
        parameters = {"station_from_id": 0,
                      "station_to_id": 0,
                      "city_from_id": city_from,
                      "city_to_id": city_to,
                      "date": date}
        response = requests.get(request_url, params=parameters)
        response = json.loads(response.text)

        if response["result"] == "success":
            soup = bs4(response["html"], "html.parser")
            uls = soup.findAll('ul', class_="sheduleRow")
            tours = []
            for i_ul, ul in enumerate(uls):
                lis = ul.findAll("li")
                departure_time = lis[0].text.lstrip().split(' ')[0]
                arrival_time = lis[1].text.split(' ')[0]
                free_space = lis[2].text
                price = lis[3].text.split(' ')[0][:-1]
                tours.append({"Отправление": departure_time,
                              "Прибытие": arrival_time,
                              "Свободно": free_space,
                              "Цена": price})
            return tours
        else:
            return response["errors"]

    def _get_info_api(self):
        city_from = self.city_mapping.get(self.city_from)
        city_to = self.city_mapping.get(self.city_to)
        date = self.date
        request_url = "https://xn--90aiim0b.xn--80aa3agllaqi6bg.xn--90ais/api/v1/client/route/tours"
        parameters = {"from": city_from,
                      "to": city_to,
                      "date": datetime.datetime.strptime(date, "%d.%m.%Y").timestamp(),
                      "count_places": 1}
        response = requests.get(request_url, params=parameters)
        response = json.loads(response.text)
        tours = []

        for tour in response["tours"]:
            date_start = self._transform_date(datetime.datetime.fromisoformat(tour["date_start"]))
            date_finish = self._transform_date(datetime.datetime.fromisoformat(tour["date_finish"]))
            route_interval = "{}:{}".format(*divmod(tour["route_interval"], 60))

            tours.append({"Маршрут": tour["route_name"],
                          "Отправление": date_start,
                          "В пути": route_interval,
                          "Прибытие": date_finish,
                          "Цена": tour["price"]})

        return tours

    def get_info(self):
        tours = self._get_info_api()
        response = []
        if isinstance(tours, list):
            for number, tour in enumerate(tours):
                response.append(f"\nВариант №{number + 1}:")
                for k, v in tour.items():
                    response.append(f"{k}: {v}")
        elif isinstance(tours, dict):
            response.append("Ошибка! Надеюсь, это как-нибудь поможет :\\")
            for k, v in tours.items():
                v = ','.join(v)
                response.append(f"{k}: {v}")
        response = '\n'.join(response)
        return response
