import json
import market
import smtplib
import configparser


config = configparser.ConfigParser()
config_f_name = 'email.ini'
try:
    config.read(config_f_name)
    config['email']['email']  # try to read data
except:
    config['email'] = {
        'email': 'email@example.com',
        'password': 'password1234',

        'to_addr': 'myemail@gmail.com',
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

with open('items.json') as f:
    items = json.load(f)


output = 'PRICES BELOW\n'
threshold_reached = False
for k in items:
    orders = market.get_orders(k['name'])
    suitable = market.apply_filters(
        orders,
        k['filters']
    )

    # with open(f'data/{k}.json', 'w') as f:
    #     json.dump(suitable, f, indent=4)

    prices = [o['platinum'] for o in suitable]

    low = int(prices[0] + 0.5)
    avg = int(market.average(prices) + 0.5)
    avg_30_percent = int(market.average(prices[:int(len(prices) * 0.3 + 0.5)]) + 0.5)
    med = int(market.median(prices) + 0.5)
    med_30_percent = int(market.median(prices[:int(len(prices) * 0.3 + 0.5)]) + 0.5)

    target_status = f'below {k["target_sell_price"]} platinum'
    if avg_30_percent >= k['target_sell_price']:
        threshold_reached = True
        target_status = f'REACHED {k["target_sell_price"]} platinum!'

    output += f'''{k['name']}: {target_status}
    lowest  :   {low}p

    30% avg :   {avg_30_percent}p
    30% med :   {med_30_percent}p

    all avg :   {avg}p
    all med :   {med}p\n\n'''

subject = 'SCRIPT: warframe.market'
if threshold_reached:
    subject += ' - At least 1 item is above sell threshold'

email = {
    'subject': subject,
    'body': output
}

send_email(config, email)
