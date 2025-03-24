#
# Configure default values for the backend
#
##############################################################################

API_PORT            = '15651'
SERVER_NAME         = 'cloudflare-s2s server'
AUTOCONNECT         = True
BUILD_DATE_FILE     = "/build-date.txt"
VERSION             = "0.1"    #TODO: import from a global defaults !
CONFIG_FILENAME     = "/var/data/backend_config.cfg"
SERVER_NAME         = "cloudflare-s2s"

#_DEFAULT_CLOUDFLARE_IP_RANGE = '100.96.0.1-25'
CLOUDFLARE_IP_RANGE = '100.96.0.1-254'