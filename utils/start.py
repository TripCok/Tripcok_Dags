import time

from AS1 import run as r_l
from AS2 import run as r_l_g
from AS3 import run as r_l_g_a
while True:
    r_l()
    time.sleep(1)
    r_l_g()
    time.sleep(1)
    r_l_g_a()
    time.sleep(10)

