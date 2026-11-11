"""
Copyright start
MIT License
Copyright (c) 2026 Fortinet Inc
Copyright end
"""

import requests
from datetime import datetime
from connectors.core.connector import get_logger, ConnectorError
from .constants import *

logger = get_logger('manage-engine-log360')


class ManageEngine:
    def __init__(self, config):
        self.server_url = config.get('server_url').strip('/')
        if not self.server_url.startswith('https://') and not self.server_url.startswith('http://'):
            self.server_url = 'https://' + self.server_url
        self.token = config.get('token')
        self.verify_ssl = config.get('verify_ssl')

    def make_api_call(self, endpoint=None, params=None, method='GET', data=None):
        url = '{0}{1}{2}'.format(self.server_url, '/api/v2/', endpoint)
        logger.debug('Request URL {0}'.format(url))
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.token)
        }
        logger.debug("Headers: {0}".format(headers))
        logger.debug("Query Parameters: {0}".format(params))
        logger.debug("Payload: {0}".format(data))
        try:
            response = requests.request(method=method, url=url,
                                        params=params, headers=headers, json=data, verify=self.verify_ssl, timeout=60)
            logger.debug("Response: {0}".format(response.text))
            if response.status_code in [200, 201, 204]:
                if response.text != "" and 'ERROR_DESCRIPTION' in response.text:
                    err_resp = response.json()
                    failure_msg = err_resp['ERROR_DESCRIPTION']
                    error_msg = 'Response [{0}: Details: {1}]'.format(response.status_code,
                                                                      failure_msg if failure_msg else '')
                    logger.error(error_msg)
                    raise ConnectorError(error_msg)
                elif response.text != "":
                    return response.json()
                else:
                    return True
            elif response.status_code == 404:
                return response
            else:
                failure_msg = response.reason
                if response.text != "" and 'ERROR_DESCRIPTION' in response.text:
                    failure_msg = response.json()['ERROR_DESCRIPTION']
                error_msg = 'Response [{0}:{1}]'.format(response.status_code, failure_msg)
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
        meta = resp.get("meta", {})

        if meta.get("total_items") == meta.get("items_in_current_page"):
            if "cursor" in resp["meta"]:
                del resp["meta"]["cursor"]
            return resp

        if isinstance(resp.get("data"), dict):
            search_result = resp.get("data", {}).get("hits", [])
            data_key = "hits"
        else:
            search_result = resp.get("data", [])
            data_key = None

        while meta.get("cursor"):
            next_resp = self.make_api_call(
                endpoint,
                data={"cursor": meta["cursor"]}
            )

            if data_key == "hits":
                search_result.extend(next_resp.get("data", {}).get("hits", []))
            else:
                search_result.extend(next_resp.get("data", []))

            meta = next_resp.get("meta", {})
            resp = next_resp

        if data_key == "hits":
            resp["data"]["hits"] = search_result
        else:
            resp["data"] = search_result
        if "cursor" in resp["meta"]:
            del resp["meta"]["cursor"]
        return resp


def build_params(params):
    return {k: v for k, v in params.items() if v is not None and v != ''}


def convert_datetime_to_log360_format(date_time):
    output_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%dT%H:%M:%SZ")
    return output_time


def invoke_search(config, params):
    me = ManageEngine(config)
    endpoint = 'search'
    log_source_ids = params.get('log_source_ids')
    if isinstance(log_source_ids, str):
        log_source_ids = [int(x.strip()) for x in log_source_ids.split(",")] if log_source_ids else []
    log_types = params.get('log_types')
    if log_types and isinstance(log_types, str):
        log_types = log_types.split(",")
    log_source_group_ids = params.get('log_source_group_ids')
    if isinstance(log_source_group_ids, str):
        log_source_group_ids = [int(x.strip()) for x in log_source_group_ids.split(",")] if log_source_group_ids else []
    payload = {
        "query": params.get('query'),
        "start_time": convert_datetime_to_log360_format(params.get('from')),
        "end_time": convert_datetime_to_log360_format(params.get('to')),
        "log_source_ids": log_source_ids,
        "log_types": log_types,
        "log_source_group_ids": log_source_group_ids,
        "response_type": params.get('response_type').lower() if params.get('response_type') else None
    }
    payload = build_params(payload)
    response = me.make_api_call(endpoint, method="POST", data=payload)
    return me.get_all_records(response, endpoint)


def get_alerts(config, params):
    me = ManageEngine(config)
    endpoint = 'alerts'
    alert_profiles = params.get('alert_profiles')
    if isinstance(alert_profiles, str):
        alert_profiles = [int(x.strip()) for x in alert_profiles.split(",")] if alert_profiles else []
    payload = {
        "query": params.get('query'),
        "start_time": convert_datetime_to_log360_format(params.get('from')),
        "end_time": convert_datetime_to_log360_format(params.get('to')),
        "profile_ids": alert_profiles,
        "severity": ",".join(value.lower() for value in params.get("severity")) if params.get("severity") else "",
        "status": ",".join(EVENT_STATUS.get(value) for value in params.get("status")) if params.get("status") else "",
        "response_type": params.get('response_type').lower() if params.get('response_type') else None
    }
    payload = build_params(payload)
    response = me.make_api_call(endpoint, method="POST", data=payload)
    return me.get_all_records(response, endpoint)


def get_alert_profiles(config, params):
    me = ManageEngine(config)
    query_parameters = {
        "profile_type": ALERT_PROFILE_TYPE.get(params.get('type')) if params.get('type') else None,
        "severity": params.get('severity').lower() if params.get('severity') else None,
        "status": params.get('status').lower() if params.get('status') else None,
        "from": params.get('from'),
        "limit": params.get('limit'),
        "response_type": params.get('response_type').lower() if params.get('response_type') else None
    }
    params = build_params(query_parameters)
    endpoint = 'alerts/profile'
    response = me.make_api_call(endpoint, params=params)
    return response


def get_incidents_list(config, params):
    me = ManageEngine(config)
    query_parameters = {
        "created_by": params.get('created_by') if params.get('created_by') else None,
        "assignee": params.get('assignee') if params.get('assignee') else None,
        "severity": ",".join(value.lower() for value in params.get("severity")) if params.get("severity") else "",
        "status": ",".join(EVENT_STATUS.get(value) for value in params.get("status")) if params.get("status") else "",
        "from": params.get('from'),
        "limit": params.get('limit'),
        "response_type": params.get('response_type').lower() if params.get('response_type') else None
    }
    params = build_params(query_parameters)
    endpoint = 'incident'
    response = me.make_api_call(endpoint, params=params)
    return response


def get_incident_details(config, params):
    me = ManageEngine(config)
    endpoint = 'incident/{0}'.format(params.get('incident_id'))
    response = me.make_api_call(endpoint)
    return response


def execute_an_api_request(config, params):
    me = ManageEngine(config)
    endpoint = params.get("endpoint")
    http_method = params.get("method")
    query_params = params.get("params") if params.get("params") else None
    payload = params.get("data") if params.get("data") else None
    response = me.make_api_call(method=http_method, endpoint=endpoint, data=payload, params=query_params)
    return response


def check_health(config):
    try:
        me = ManageEngine(config)
        params = {"limit": 1}
        endpoint = 'alerts/profile'
        response = me.make_api_call(endpoint, params=params)
        if response:
            return True
    except Exception as Err:
        logger.exception('Error occurred while connecting server: {}'.format(str(Err)))
        raise ConnectorError('Error occurred while connecting server: {}'.format(Err))


operations = {
    'invoke_search': invoke_search,
    'get_alerts': get_alerts,
    'get_alert_profiles': get_alert_profiles,
    'get_incidents_list': get_incidents_list,
    'get_incident_details': get_incident_details,
    'execute_an_api_request': execute_an_api_request
}
