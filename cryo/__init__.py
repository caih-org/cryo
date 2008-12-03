import pkg_resources
import logging
import logging.config


filename = pkg_resources.resource_filename('cryo', 'conf/logging.conf')
logging.config.fileConfig(filename)
