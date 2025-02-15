#
#
###########################################################################################
# pylint: disable=logging-fstring-interpolation


from . import defaults

def get_builddate() -> str :
    ret_str = "unknown"
    with open(defaults.BUILD_DATE_FILE, "r",encoding="utf-8") as file:
        ret_str = file.read().strip()
    return ret_str