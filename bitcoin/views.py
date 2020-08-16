import json
from datetime import datetime

from django.http import HttpResponse
from rest_framework.decorators import api_view

import requests

COINGECKO_DAYS_AGO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
COINGECKO_RANGE_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
COIN_ID = "bitcoin"
USD_CURRENCY = "usd"


@api_view(['GET'])
def get_ping():
    response_body = {"success": "true"}
    response = HttpResponse(json.dumps(response_body), content_type="application/json", status=200)
    return response


@api_view(['GET'])
def get_price_chart(request):
    try:
        datetime_from = request.GET.get('from', False)
        datetime_to = request.GET.get('to', False)
        days = request.GET.get('days', 1)

        if datetime_from and datetime_to:
            price_list = get_range_price(datetime_from, datetime_to)
        elif not datetime_from and not datetime_to:
            price_list = get_days_ago_price(days)
        else:
            return HttpResponse(json.dumps({"message": "Invalid request"}), content_type="application/json", status=400)

        if type(price_list) == HttpResponse:
            return price_list

        res_body = {"number_of_prices": len(price_list), "prices": price_list}
        response = HttpResponse(json.dumps(res_body), content_type="application/json", status=200)
        return response
    except Exception as e:
        print(f"Exception {e}")
        return HttpResponse(json.dumps({"message": "Failed processing request"}), content_type="application/json",
                            status=500)


def get_range_price(datetime_from, datetime_to):
    if not validate_timestamp(datetime_from) or not validate_timestamp(datetime_to):
        return HttpResponse(json.dumps({"message": "Invalid request"}), content_type="application/json", status=400)

    params = {"vs_currency": USD_CURRENCY, "from": datetime_from, "to": datetime_to}
    res = requests.get(url=COINGECKO_RANGE_URL, params=params)
    data = {}
    if res.status_code == 200:
        data = res.json()
    return data.get("prices", [])


def get_days_ago_price(days):
    if not validate_day(days):
        return HttpResponse(json.dumps({"message": "Invalid request"}), content_type="application/json", status=400)

    params = {"vs_currency": USD_CURRENCY, "days": days}
    res = requests.get(url=COINGECKO_DAYS_AGO_URL, params=params)
    data = {}
    if res.status_code == 200:
        data = res.json()
    return data.get("prices", [])


def convert_datetime_to_unix_timestamp(datetimestamp):
    if type(datetimestamp) == datetime:
        return datetime.timestamp(datetimestamp)
    else:
        raise ValueError("Invalid datetime")


def convert_unix_timestamp_to_datetime(unix_timestamp):
    if unix_timestamp == float:
        return datetime.fromtimestamp(int(unix_timestamp)).strftime("%d/%m/%Y %H:%M:%S")
    raise ValueError("Invalid unix timestamp")


def validate_day(day):
    try:
        if int(day) > 0:
            return True
        return False
    except ValueError:
        return False


def validate_timestamp(unix_timestamp):
    try:
        if float(unix_timestamp) and float(unix_timestamp) > 17999:
            return True
        else:
            return False
    except ValueError:
        return False
