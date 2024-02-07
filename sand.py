from datetime import datetime

d, h = datetime.today(), datetime.now() 

print(h)
print(f'{d.day}/{d.month}/{d.year}')

import datetime
print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))