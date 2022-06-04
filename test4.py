from requests import request

currency_list = request("GET", "https://api.interkassa.com/v1/currency").json()


print(currency_list)