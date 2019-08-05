import os
import textwrap
import stat
from crontab import CronTab


def make_file(uidwell, uidwellbore, data_frequency, url, username, password, cron_run):
    filepath = os.getcwd()

    # temp_path = filepath + uidwell + ".py"
    file_path = "/var/www/html/SSES-Backend/backend/astra/" + uidwell + ".py"
    with open(file_path, "w+") as f:
        f.write(textwrap.dedent('''\
            #! /var/www/html/SSES-Backend/backend/env/bin/python3
            
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
    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IEXEC)

    manage_cron(uidwell, cron_run)
    print('Execution completed.')


def manage_cron(uidwell, cron_run):
    file_full_path = "/var/www/html/SSES-Backend/backend/astra/" + uidwell + ".py"

    my_cron = CronTab(user="www-data")

    # Create a cron job
    if cron_run:
        job = my_cron.new(command=file_full_path)
        job.minute.every(1)

    # Cancel a cron job
    else:
        for job in my_cron:
            if job.command == file_full_path:
                my_cron.remove(job)

    my_cron.write()
