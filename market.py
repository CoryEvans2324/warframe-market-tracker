import requests

def get_orders(item):
    url = f'https://api.warframe.market/v1/items/{item}/orders?include=item'
    try:
        r = requests.get(url)
        orders = r.json()['payload']['orders']
        return sorted(orders, key=lambda order: order['platinum'])
    except Exception as e:
        print('failed to get orders', e)

    return {}

def apply_filters(orders, dict_of_filters):
    for key, value in dict_of_filters.items():
        if isinstance(value, dict):  # to filter the user data
            for key_2, value_2 in value.items():
                orders = [o for o in orders if o[key][key_2] == value_2]
        else:
            orders = [o for o in orders if o[key] == value]

    return orders

def average(l):
    return sum(l) / len(l)


def median(l):
    length = len(l)

    if length % 2 == 0:
        return average(( l[length // 2 - 1], l[length // 2]))

    return l[length // 2]
