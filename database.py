import psycopg2

class Database:
    def __init__(self, config):
        self.connection = psycopg2.connect(
            host=config['database']['host'],
            port=config['database']['port'],
            database=config['database']['db_name'],
            user=config['database']['user'],
            password=config['database']['password']
        )

        self.cursor = self.connection.cursor()

    def upload_orders(self, item_name, order_list):
        columns_raw = [
            'order_id',
            'item_name',
            'quantity',
            'order_type',
            'platinum',
            'last_update'
        ]

        for o in order_list:
            columns = columns_raw.copy()
            formatted_order = [
                o['id'],  # order_id
                item_name,
                o['quantity'],
                o['order_type'],
                o['platinum'],
                o['last_update']
            ]

            if 'mod_rank' in o:
                columns.append('mod_rank')
                formatted_order.append(o['mod_rank'])

            columns_str = ', '.join(columns)
            values_str = ', '.join('%s' for f in formatted_order)
            if_update_set = ', '.join(f'{c} = \'{v}\'' for c, v in zip(columns[1:], formatted_order[1:]))

            sql_query = f'insert into orders ({columns_str}) values ({values_str}) ON CONFLICT (order_id) DO UPDATE SET {if_update_set};'

            self.cursor.execute(sql_query, formatted_order)

        self.commit()
        # return sql_query

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

