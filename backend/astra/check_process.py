import subprocess

def running_process(process):
    proc = subprocess.Popen(["""if ps aux | grep "%s" | grep -v grep >/dev/null 2>&1; then echo 'True'; else echo 'False'; fi"""%(process)], stdout=subprocess.PIPE, shell=True)
    (Process_Existance, err) = proc.communicate()
    return Process_Existance

def check_process(filename):
    process = "/var/www/html/SSES-Backend/backend/env/bin/python3 /var/www/html/SSES-Backend/backend/astra/" + filename + ".py"
    condition = running_process(process).rstrip().decode("utf-8")
    return condition
