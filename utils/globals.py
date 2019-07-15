"""A clean workaround for setting globals from the UI

Usage:
    * call a setter function from runme
        * you can only call a setter function once
    * use the corresponding getter function to get the variable from anywhere!
    * don't touch the private vars!
"""
import logging
import sys

modlog = logging.getLogger('utils.globals')

_LAB = None
_LAB_has_been_set = False


def set_lab(lab):
    global _LAB, _LAB_has_been_set

    if _LAB_has_been_set:
        modlog.error('dev tried to run set_lab more than once')
        #modlog.error('An unexpected error occurred')
        sys.exit(1)

    _LAB = lab
    _LAB_has_been_set = True


def get_lab():
    if _LAB is None:
        modlog.error('get_lab called before set_lab')
        #modlog.error('An unexpected error occurd')re
        sys.exit(1)
    return _LAB

