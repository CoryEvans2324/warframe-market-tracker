import json
import market
import smtplib
import database
import configparser


config = configparser.ConfigParser()
config_f_name = 'config.ini'
try:
    config.read(config_f_name)
    config['email']['email']  # try to read data
    config['database']['host']
except:
    config['email'] = {
        'email': 'email@example.com',
        'password': 'password1234',

        'to_addr': 'myemail@gmail.com',
    }

    config['database'] = {
        'host': 'localhost',
        'port': 5432,
        'db_name': 'warframe_market',
        'user': 'postgres',
        'password': 'password'
    }

    with open(config_f_name, 'w') as f:
        config.write(f)
    print(f'Please edit: {config_f_name}')

    quit()


def send_email(config, email):
    from_addr = config['email']['email']
    to_addr = config['email']['to_addr']

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(from_addr, config['email']['password'])

    msg = f'''\
From: {from_addr}
To: {to_addr}
Subject: {email['subject']}
{email['body']}
    '''

    server.sendmail(from_addr, to_addr, msg)
    server.close()

def parse_orders(config, items, dict_of_orders):
    threshold_reached = False
    output = 'PRICES BELOW\n'
    for item_name, orders in dict_of_orders.items():
        orders = market.apply_filters(
            orders,
            items[item_name]['filters']
        )

        target_sell_price = items[item_name]['target_sell_price']


        prices = [o['platinum'] for o in orders]

        low = int(prices[0] + 0.5)
        avg = int(market.average(prices) + 0.5)
        avg_30_percent = int(market.average(prices[:int(len(prices) * 0.3 + 0.5)]) + 0.5)
        med = int(market.median(prices) + 0.5)
        med_30_percent = int(market.median(prices[:int(len(prices) * 0.3 + 0.5)]) + 0.5)


        target_status = f'below {target_sell_price} platinum'
        if avg_30_percent >= target_sell_price:
            threshold_reached = True
            target_status = f'REACHED {target_sell_price} platinum!'


        output += f'''{item_name}: {target_status}
            \r\tlowest  :   {low}p

            \r\t30% avg :   {avg_30_percent}p
            \r\t30% med :   {med_30_percent}p

            \r\tall avg :   {avg}p
            \r\tall med :   {med}p\n\n'''


    if threshold_reached:
        subject = 'SCRIPT: warframe.market - At least 1 item is above sell threshold'

        email = {
            'subject': subject,
            'body': output
        }

        send_email(config, email)

    return output



if __name__ == "__main__":
    with open('items.json') as f:
        items = json.load(f)

    db = database.Database(config)

    all_orders = market.get_all_orders(items)
    parse_orders(config, items, all_orders)

    for item_name, orders in all_orders.items():
        db.upload_orders(item_name, orders)

    db.close()

