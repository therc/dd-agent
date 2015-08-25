# stdlib
from functools import wraps
import logging
import subprocess
import tempfile

log = logging.getLogger(__name__)


# FIXME: python 2.7 has a far better way to do this
def get_subprocess_output(command, log, shell=None, stdin=None):
    """
    Run the given subprocess command and return it's output. Raise an Exception
    if an error occurs.
    """

    # Use temporary file to allow reasonable amount of output memory. When using
    # subprocess.PIPE, the PIPE has a maximum writable memory of 65,535 bytes.
    with tempfile.TemporaryFile('rw') as stdout_f:
        stderr_f = tempfile.TemporaryFile('rw')
        proc = subprocess.Popen(command, close_fds=True, shell=shell, stdin=stdin,
                                stdout=stdout_f, stderr=stderr_f)
        proc.wait()
        stderr_f.seek(0)
        err = stderr_f.read()
        stderr_f.closer()
        if err:
            log.debug("Error while running {0} : {1}".format(" ".join(command),
                                                             err))

        stdout_f.seek(0)
        output = stdout_f.read()
    return output


def log_subprocess(func):
    """
    Wrapper around subprocess to log.debug commands.
    """
    @wraps(func)
    def wrapper(*params, **kwargs):
        fc = "%s(%s)" % (func.__name__, ', '.join(
            [a.__repr__() for a in params] +
            ["%s = %s" % (a, b) for a, b in kwargs.items()]
        ))
        log.debug("%s called" % fc)
        return func(*params, **kwargs)
    return wrapper

subprocess.Popen = log_subprocess(subprocess.Popen)
