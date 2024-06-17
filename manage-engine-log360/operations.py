"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""

import requests
from datetime import datetime
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('manage-engine-log360')


class ManageEngine:
    def __init__(self, config):
        self.server_url = config.get('server_url').strip('/')
        if not self.server_url.startswith('https://') and not self.server_url.startswith('http://'):
            self.server_url = 'https://' + self.server_url
        self.token = config.get('token')
        self.verify_ssl = config.get('verify_ssl')

    def make_api_call(self, endpoint=None, params=None, method='POST', data=None):
        url = '{0}{1}{2}'.format(self.server_url, '/RestAPI/v1/', endpoint)
        logger.info('Request URL {0}'.format(url))
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.token)
        }
        try:
            response = requests.request(method=method, url=url,
                                        params=params, headers=headers, json=data, verify=self.verify_ssl)
            if response.status_code in [200, 201, 204]:
                if response.text != "":
                    return response.json()
                else:
                    return True
            elif response.status_code == 404:
                return response
            else:
                if response.text != "":
                    err_resp = response.json()
                    failure_msg = err_resp['ERROR_DESCRIPTION']
                    error_msg = 'Response [{0}:{1} Details: {2}]'.format(response.status_code, response.reason,
                                                                         failure_msg if failure_msg else '')
                else:
                    error_msg = 'Response [{0}:{1}]'.format(response.status_code, response.reason)
                logger.error(error_msg)
                raise ConnectorError(error_msg)
        except requests.exceptions.SSLError:
            logger.error('An SSL error occurred')
            raise ConnectorError('An SSL error occurred')
        except requests.exceptions.ConnectionError:
            logger.error('A connection error occurred')
            raise ConnectorError('A connection error occurred')
        except requests.exceptions.Timeout:
            logger.error('The request timed out')
            raise ConnectorError('The request timed out')
        except requests.exceptions.RequestException:
            logger.error('There was an error while handling the request')
            raise ConnectorError('There was an error while handling the request')
        except Exception as err:
            raise ConnectorError(str(err))

    def get_all_records(self, resp, endpoint):
        search_result = resp.get('results').get('hits')
        while resp.get('cursor'):
            resp = self.make_api_call(endpoint, data={"cursor": resp.get('cursor')})
            search_result.append(resp.get('results').get('hits'))
        return search_result


def build_params(params):
    return {k: v for k, v in params.items() if v is not None and v != ''}


def convert_datetime_to_epoch(date_time):
    epoch = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() * 1000
    return int(epoch)


def invoke_search(config, params):
    me = ManageEngine(config)
    params = build_params(params)
    if params.get('from') and isinstance(params.get('from'), str):
        params['from'] = convert_datetime_to_epoch(params.get('from'))
    if params.get('to') and isinstance(params.get('to'), str):
        params['to'] = convert_datetime_to_epoch(params.get('to'))
    if params.get('hosts') and isinstance(params.get('hosts'), int):
        params['hosts'] = [params.get('hosts')]
    if params.get('groups') and isinstance(params.get('groups'), int):
        params['groups'] = [params.get('groups')]
    if not params.get('query'):
        params['query'] = ''
    endpoint = 'search'
    response = me.make_api_call(endpoint, data=params)
    return me.get_all_records(response, endpoint)


def get_alerts(config, params):
    me = ManageEngine(config)
    params = build_params(params)
    if params.get('from') and isinstance(params.get('from'), str):
        params['from'] = convert_datetime_to_epoch(params.get('from'))
    if params.get('to') and isinstance(params.get('to'), str):
        params['to'] = convert_datetime_to_epoch(params.get('to'))
    if params.get('alert_profiles') and isinstance(params.get('alert_profiles'), int):
        params['alert_profiles'] = [params.get('alert_profiles')]
    endpoint = 'alerts'
    response = me.make_api_call(endpoint, data=params)
    return me.get_all_records(response, endpoint)


def get_alert_profiles(config, params):
    me = ManageEngine(config)
    params = build_params(params)
    endpoint = 'meta/alert_profiles'
    response = me.make_api_call(endpoint, data=params)
    return response


def check_health(config):
    try:
        payload = {}
        response = get_alerts(config, params=payload)
        if response:
            return True
    except Exception as Err:
        logger.exception('Error occurred while connecting server: {}'.format(str(Err)))
        raise ConnectorError('Error occurred while connecting server: {}'.format(Err))


operations = {
    'invoke_search': invoke_search,
    'get_alerts': get_alerts,
    'get_alert_profiles': get_alert_profiles
}
