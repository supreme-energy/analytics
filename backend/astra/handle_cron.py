import os
import textwrap
from crontab import CronTab


def make_file(uidwell, uidwellbore, data_frequency, url, username, password, cron_run):
    filepath = os.getcwd()

    # temp_path = filepath + file_name + ".py"
    with open(file_name + ".py", 'w') as f:
        f.write(textwrap.dedent('''\
            from wits_mapper import witsmapper
            from check_process import check_process

            UIDWELL = "%s"
            UIDWELLBORE = "%s"
            DATA_FREQUENCY = %s
            URL = "%s"
            USERNAME = "%s"
            PASSWORD = "%s"
            FILE_NAME = "%s"

            if check_process(FILE_NAME) == False:
                witsmapper(UIDWELL, UIDWELLBORE, DATA_FREQUENCY, URL, USERNAME, PASSWORD)     
                
                ''' % (uidwell, uidwellbore, data_frequency, url, username, password, uidwell)))
    print('Execution completed.')
    manage_cron(file_name, cron_run)


def manage_cron(uidwell, cron_run):
    python_env = "/var/www/html/SSES-Backend/backend/env/bin/python3"
    file_full_path = python_env + \
        " /var/www/html/SSES-Backend/backend/" + uidwell + ".py"

    my_cron = CronTab(user="www-data")

    # Create a cron job
    if cron_run:
        job = my_cron.new(command=file_full_path)
        job.minute.every(1)

    # Cancel a cron job
    else:
        my_cron.remove(command=file_full_path)

    my_cron.write()
