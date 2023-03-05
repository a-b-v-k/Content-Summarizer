# Description: Test file for the content summarizer
try:
    import tensorflow as tf
except:
    import subprocess
    subprocess.call(['pip', 'install', 'tensorflow'])