from threading import Thread
import time
import sys
from functools import wraps


class SpinCursor:
    """ A console spin cursor class """

    def __init__(self, prefix='', suffix=''):
        self.prefix = prefix
        self.suffix = suffix
        self.sequence = ('   ', '.  ', '.. ', '...')

    def spin(self):
        """ Perform a single spin """
        for x in self.sequence:
            print(f'\r{self.prefix}{x}{self.suffix}', end='')
            time.sleep(0.3)

    def run(self):
        while True:
            self.spin()


def spinner(prefix='', suffix=''):
    def wrapper_outer(func):
        @wraps(func)
        def wrapper_inner(*args, **kwargs):
            # FIXME: make the spinner work
            # spin = SpinCursor(prefix=prefix, suffix=suffix)
            # t = Thread(target=spin.run, daemon=True)
            # t.start()
            print(f'{prefix}...{suffix}')
            result = func(*args, **kwargs)
            return result
        return wrapper_inner
    return wrapper_outer
