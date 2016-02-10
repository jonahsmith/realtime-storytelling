import sys
import time

while True:
    # Test the 'good' range
    print('{"p25": 10, "update_time": "2016-02-09 14:00"}')
    sys.stdout.flush()
    time.sleep(5)
    # Test the 'moderate' range
    print('{"p25": 20, "update_time": "2016-02-09 15:00"}')
    sys.stdout.flush()
    time.sleep(5)
    # Test the 'unhealthy for certain groups' range
    print('{"p25": 40, "update_time": "2016-02-09 16:00"}')
    sys.stdout.flush()
    time.sleep(5)
    # Test the 'unhealthy' range
    print('{"p25": 60, "update_time": "2016-02-09 17:00"}')
    sys.stdout.flush()
    time.sleep(10)
