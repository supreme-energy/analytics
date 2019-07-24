#! /var/www/html/SSES-Backend/backend/env/bin/python3

from wits_mapper import witsmapper
from check_process import check_process

UIDWELL = "ae7ad273-cba4-44ce-a936-20fca8d354a6"
UIDWELLBORE = "ed636b32-2ff9-4546-acd0-481ac83d6256"
DATA_FREQUENCY = 10
URL = "http://witsml.polarisguidance.com:8081/services/polarisWMLS"
USERNAME = "sses_us"
PASSWORD = "PolarisTexas"
FILE_NAME = "job_3"

if check_process(FILE_NAME) == "False":
    witsmapper(UIDWELL, UIDWELLBORE, DATA_FREQUENCY, URL, USERNAME, PASSWORD)
