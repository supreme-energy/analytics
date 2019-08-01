import subprocess


def running_process(process):
    proc = subprocess.Popen(
        ["""ps aux | grep "%s" | grep -v grep | awk '{print $2}'""" % (process)], stdout=subprocess.PIPE, shell=True)
    (Process_Existance, err) = proc.communicate()
    overall_proc = Process_Existance.rstrip().decode("utf-8")
    proc_length = len(overall_proc)
    two_processes = True if proc_length > 7 else False
    return two_processes


def check_process(filename):
    process = "/var/www/html/SSES-Backend/backend/env/bin/python3 /var/www/html/SSES-Backend/backend/astra/" + filename + ".py"
    condition = running_process(process)
    return condition
