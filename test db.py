
from dbt import *


db = Db()
#
# db.add_data({'id': '1.1.1.1', 'data': '1002'})
# db.add_sensor('1.1.1.2')
#
#
# print(db.get_data())
# print('---')
#
# print(db.get_sensor())
# print('---')
#
# print(db.get_history())

db.clear_db_file()
