import numpy as np
from time import sleep
from test_common import *
import logging
import os
logging.basicConfig(filename="log.txt", level=logging.DEBUG, filemode='w', 
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',)

def get_sonata_path():
    import subprocess
    result = subprocess.run(['blkid', '-l', '-o', 'device', '-t', 
                             'LABEL=SONATA', '-c', '/dev/null'],
                             capture_output=True)
    mnt = result.stdout.decode().strip()
    result = subprocess.run(['findmnt', mnt, '-no', 'TARGET'], capture_output=True)
    return result.stdout.decode().strip()


#sonata_path = "../../sonata" #TODO: make this better
sonata_path = get_sonata_path()
os.sync()
print("Copying sonata.bit...")
copy_sonata_bitstream(sonata_path)
os.sync() #ensure above write finishes

print ("Done copy. Testing config write and parse...")

write_all_options(sonata_path)
os.sync() #ensure above write finishes

print("Done. Ejecting drive...")
sleep(0.25)

print("Copying firmware")
copy_firmware(sonata_path)
os.sync()


results, full_file = get_test_results(sonata_path)
intended_failures = (3, 4) # these ones check to make sure invalid 
any_failures = 0
for num, result in enumerate(results):
    if num in intended_failures:
        if result['passed']:
            print("Passed test that should have failed {}".format(str(result)))
            any_failures = 1
        else:
            print("Passed test {}".format(str(result['name'])))
    else:
        if not result['passed']:
            print("Failed test {}".format(str(result)))
            any_failures = 1
        else:
            print("Passed test {}".format(str(result['name'])))

with open('LOG.TXT', "w") as f:
    f.write(str(full_file))

if not any_failures:
    print("All tests passed")
# print(full_file)