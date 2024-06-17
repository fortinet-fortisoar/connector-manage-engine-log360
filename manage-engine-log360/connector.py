"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""


from connectors.core.connector import Connector
from connectors.core.connector import get_logger, ConnectorError
from .operations import operations, check_health


logger = get_logger('manage-engine-log360')


class ManageEngine(Connector):
    def execute(self, config, operation, params, **kwargs):
        try:
            operation = operations.get(operation)
            return operation(config, params)
        except Exception as Err:
            logger.error('Exception occurred: {}'.format(Err))
            raise ConnectorError(Err)

    def check_health(self, config):

        return check_health(config)
