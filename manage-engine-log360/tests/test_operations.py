# Edit the config_and_params.json file and add the necessary parameter values.
    
import os
import sys
import json
import pytest
import logging
import importlib
from connectors.core.connector import ConnectorError

with open('tests/config_and_params.json', 'r') as file:
    params = json.load(file)

current_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
grandparent_directory = os.path.abspath(os.path.join(parent_directory, os.pardir))
sys.path.insert(0, str(grandparent_directory))

module_name = 'manage-engine-log360_1_0_0.operations'
conn_operations_module = importlib.import_module(module_name)
operations = conn_operations_module.operations

with open('info.json', 'r') as file:
    info_json = json.load(file)

logger = logging.getLogger(__name__)
    

# To test with different configuration values, adjust the index in the list below.
@pytest.fixture(scope="module")
def valid_credentials():
    return params.get('config')[0]
    
    
@pytest.fixture(scope="module")
def valid_credentials_with_token(valid_credentials):
    config = valid_credentials.copy()
    operations['check_health'](config)
    return config
    

@pytest.mark.checkhealth     
def test_check_health_success(valid_credentials):
    assert operations['check_health'](valid_credentials.copy())   
    

@pytest.mark.checkhealth     
def test_check_health_invalid_server_url(valid_credentials):
    # update server_url with an invalid value
    invalid_creds = valid_credentials.copy()
    invalid_creds['server_url'] = 'http://10.132.254.158:8400'
    with pytest.raises(ConnectorError):
        assert operations['check_health'](invalid_creds)
    

@pytest.mark.checkhealth     
def test_check_health_invalid_token(valid_credentials):
    # update token with an invalid value
    invalid_creds = valid_credentials.copy()
    invalid_creds['token'] = 'cedfwersf'
    with pytest.raises(ConnectorError):
        assert operations['check_health'](invalid_creds)
    

# Ensure that all mandatory parameters (if any) are provided.
@pytest.mark.invoke_search
@pytest.mark.parametrize("input_params", params['invoke_search'])
def test_invoke_search_success(valid_credentials_with_token, input_params):
    logger.info("params: {0}".format(input_params))
    assert operations['invoke_search'](valid_credentials_with_token, input_params)
  
    
# Ensure that the provided input_params yield the correct output schema, or adjust the index in the list below.
@pytest.mark.invoke_search
@pytest.mark.schema_validation
def test_validate_invoke_search_output_schema(valid_credentials_with_token):
    input_params = params.get('invoke_search')[0]
    logger.info("params: {0}".format(input_params))
    schema = {}
    for operation in info_json.get("operations"):
        if operation.get('operation') == 'invoke_search':
            schema = operation.get('output_schema')
            break
    logger.info("output_schema: {0}".format(schema))
    assert operations['invoke_search'](valid_credentials_with_token, input_params).keys() == schema.keys()
    

@pytest.mark.invoke_search     
def test_invoke_search_invalid_from(valid_credentials_with_token):
    input_params = params.get('invoke_search')[0].copy()
    # update from with an invalid value
    input_params['from'] = '10:45:30'
    with pytest.raises(ValueError):
        assert operations['invoke_search'](valid_credentials_with_token, input_params)
    

@pytest.mark.invoke_search     
def test_invoke_search_invalid_to(valid_credentials_with_token):
    input_params = params.get('invoke_search')[0].copy()
    # update to with an invalid value
    input_params['to'] = '10:45:30'
    with pytest.raises(ValueError):
        assert operations['invoke_search'](valid_credentials_with_token, input_params)
    

@pytest.mark.invoke_search     
def test_invoke_search_invalid_hosts(valid_credentials_with_token):
    input_params = params.get('invoke_search')[0].copy()
    # update hosts with an invalid value
    input_params['hosts'] = 'vcwrfv'
    with pytest.raises(ConnectorError):
        assert operations['invoke_search'](valid_credentials_with_token, input_params)
    

@pytest.mark.invoke_search     
def test_invoke_search_invalid_groups(valid_credentials_with_token):
    input_params = params.get('invoke_search')[0].copy()
    # update groups with an invalid value
    input_params['groups'] = 'ceadc'
    with pytest.raises(ConnectorError):
        assert operations['invoke_search'](valid_credentials_with_token, input_params)


@pytest.mark.invoke_search
def test_invoke_search_invalid_query(valid_credentials_with_token):
    input_params = params.get('invoke_search')[0].copy()
    # update query with an invalid value
    input_params['query'] = '!@#$%^&*()'
    with pytest.raises(ConnectorError):
        assert operations['invoke_search'](valid_credentials_with_token, input_params)
    

# Ensure that all mandatory parameters (if any) are provided.
@pytest.mark.get_alerts
@pytest.mark.parametrize("input_params", params['get_alerts'])
def test_get_alerts_success(valid_credentials_with_token, input_params):
    logger.info("params: {0}".format(input_params))
    assert operations['get_alerts'](valid_credentials_with_token, input_params)
  
    
# Ensure that the provided input_params yield the correct output schema, or adjust the index in the list below.
@pytest.mark.get_alerts
@pytest.mark.schema_validation
def test_validate_get_alerts_output_schema(valid_credentials_with_token):
    input_params = params.get('get_alerts')[0]
    logger.info("params: {0}".format(input_params))
    schema = {}
    for operation in info_json.get("operations"):
        if operation.get('operation') == 'get_alerts':
            schema = operation.get('output_schema')
            break
    logger.info("output_schema: {0}".format(schema))
    assert operations['get_alerts'](valid_credentials_with_token, input_params).keys() == schema.keys()
    

@pytest.mark.get_alerts     
def test_get_alerts_invalid_from(valid_credentials_with_token):
    input_params = params.get('get_alerts')[0].copy()
    # update from with an invalid value
    input_params['from'] = 'efqqdcs'
    with pytest.raises(ValueError):
        assert operations['get_alerts'](valid_credentials_with_token, input_params)
    

@pytest.mark.get_alerts     
def test_get_alerts_invalid_to(valid_credentials_with_token):
    input_params = params.get('get_alerts')[0].copy()
    # update to with an invalid value
    input_params['to'] = 'cadcadf'
    with pytest.raises(ValueError):
        assert operations['get_alerts'](valid_credentials_with_token, input_params)
    

@pytest.mark.get_alerts     
def test_get_alerts_invalid_alert_profiles(valid_credentials_with_token):
    input_params = params.get('get_alerts')[0].copy()
    # update alert_profiles with an invalid value
    input_params['alert_profiles'] = 'cadc'
    with pytest.raises(ConnectorError):
        assert operations['get_alerts'](valid_credentials_with_token, input_params)
    

# Ensure that all mandatory parameters (if any) are provided.
@pytest.mark.get_alert_profiles
@pytest.mark.parametrize("input_params", params['get_alert_profiles'])
def test_get_alert_profiles_success(valid_credentials_with_token, input_params):
    logger.info("params: {0}".format(input_params))
    assert operations['get_alert_profiles'](valid_credentials_with_token, input_params)
  
    
# Ensure that the provided input_params yield the correct output schema, or adjust the index in the list below.
@pytest.mark.get_alert_profiles
@pytest.mark.schema_validation
def test_validate_get_alert_profiles_output_schema(valid_credentials_with_token):
    input_params = params.get('get_alert_profiles')[0]
    logger.info("params: {0}".format(input_params))
    schema = {}
    for operation in info_json.get("operations"):
        if operation.get('operation') == 'get_alert_profiles':
            schema = operation.get('output_schema')
            break
    logger.info("output_schema: {0}".format(schema))
    assert operations['get_alert_profiles'](valid_credentials_with_token, input_params).keys() == schema.keys()
    
