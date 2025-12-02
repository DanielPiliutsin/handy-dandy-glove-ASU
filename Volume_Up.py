import subprocess

def increase_volume():
    subprocess.run(["amixer", "set", "Master", "5%+"])
    subprocess.run(["espeak", "'Turning Volume up!'"])
increase_volume()
