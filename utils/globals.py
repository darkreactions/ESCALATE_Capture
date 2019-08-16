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
_SAMPLER = None
_SAMPLERVERSION = None
_SAMPLER_UID = None
_SAMPLER_has_been_set = False


def set_lab(lab):
    global _LAB, _LAB_has_been_set

    if _LAB_has_been_set:
        modlog.error('dev tried to run set_lab more than once')
        sys.exit(1)

    _LAB = lab
    _LAB_has_been_set = True


def get_lab():
    if _LAB is None:
        modlog.error('get_lab called before set_lab')
        sys.exit(1)
    return _LAB


def set_sampler(sampler_name, version):
    ''' sets the name and version of the sampler as the sampler UID

    :param sampler_name: name of the method used for samplng
    :param version: version of the method used for sampling reported
                    by the sampling function
    :returns: **no returns, call func get_sampler_uid
    '''
    global _SAMPLER, _SAMPLER_has_been_set, _SAMPLER_UID

    _SAMPLER = sampler_name
    _SAMPLERVERSION = version
    _SAMPLER_UID = 'escalate_' + str(sampler_name) + '_' + str(version)

    _SAMPLER_has_been_set = True


def get_sampler_uid():
    '''returns the sampler used for automated sampling
    '''
    global _SAMPLER_UID
    if _SAMPLER is None:
        modlog.error('get_sampler_uid called before set_sampler')
        sys.exit(1)
    return _SAMPLER_UID


def get_sampler_author():
    import devconfig
    sampler_author = 'escalate_' + str(devconfig.RoboVersion)
    return(sampler_author)


def get_user_author_name():
    message = ("Enter the name you would like to appear for manual submissions (e.g., Ian Pendleton):")
    user_input = input(message)

    with open('./capture/user_cli_variables.py', 'w') as fout:
        fout.write("# This file acts as a local cache to the user's preferred author name\n")
        fout.write("user_author_name = '%s'\n" % user_input)
    # import the repo_path from the python file cache we just created
    from capture.user_cli_variables import user_author_name
    return user_author_name


def get_manualruns_uid():
    manual_run_uid = 'escalate_ManualSpecification_1'
    return manual_run_uid


def get_manualruns_author():
    try:
        from capture.user_cli_variables import user_author_name
    except ModuleNotFoundError:
        user_author_name = get_user_author_name()
    return user_author_name
