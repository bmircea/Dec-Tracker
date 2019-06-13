import os
import shutil
import subprocess


if os.getenv('PDFTK_PATH'):
    PDFTK_PATH = os.getenv('PDFTK_PATH')
else:
    PDFTK_PATH = '/usr/bin/pdftk'
    if not os.path.isfile(PDFTK_PATH):
        PDFTK_PATH = 'pdftk'


def check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output

def run_command(command, shell=False):
    ''' run a system command and yield output '''
    p = check_output(command, shell=shell)
    return p.split(b'\n')

def unpack(pdf_path, output):
    ''' unpack pdf to get the XML '''
    cmd = "%s %s unpack_files %s" % (PDFTK_PATH, pdf_path, output)
    run_command(cmd)
