import re
import typing
import json
import yaml
import xml
import datetime
import urllib


def transformer_src_endpoint_ip(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract source IP address (first field in Apache log)
        match = re.match(r'^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return the IP address as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_time(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract timestamp from Apache log format [22/Dec/2016:16:36:02 +0300]
        match = re.search(r'\[([^\]]+)\]', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Convert Apache timestamp to epoch time
        if extracted_values:
            timestamp_str = extracted_values[0]
            # Parse format: 22/Dec/2016:16:36:02 +0300
            dt = datetime.datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            return str(int(dt.timestamp() * 1000))  # Return milliseconds
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_request_http_method(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract HTTP method from request line
        match = re.search(r'\] (GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|CONNECT) ', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return HTTP method as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_activity_id(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract HTTP method and map to activity_id
        match = re.search(r'\] (GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|CONNECT) ', input_entry)
        if match:
            method = match.group(1)
            # Map HTTP methods to OCSF activity_id values
            method_map = {
                'GET': '3',
                'POST': '6',
                'DELETE': '2',
                'HEAD': '4',
                'OPTIONS': '5',
                'PUT': '7',
                'TRACE': '8',
                'CONNECT': '1'
            }
            return [method_map.get(method, '99')]  # Default to 'Other'
        return ['0']  # Unknown

    def transform(extracted_values: typing.List[str]) -> str:
        # Return activity_id as-is
        if extracted_values:
            return extracted_values[0]
        return '0'

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_request_url_url_string(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract full URL path and query string from request line
        match = re.search(r'\] (?:GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|CONNECT) ([^ ]+) HTTP', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return URL string as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_request_url_path(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract URL path (without query string) from request line
        match = re.search(r'\] (?:GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|CONNECT) ([^?\s]+)', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return path as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_request_url_query_string(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract query string from request line
        match = re.search(r'\] (?:GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|CONNECT) [^?\s]+\?([^\s]+) HTTP', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return query string as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_request_version(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract HTTP version from request line
        match = re.search(r'(HTTP/[0-9]+\.[0-9]+)', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return HTTP version as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_response_code(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract HTTP status code (after HTTP version)
        match = re.search(r'HTTP/[0-9]+\.[0-9]+ ([0-9]+)', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return status code as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_response_length(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract response length (after status code)
        match = re.search(r'HTTP/[0-9]+\.[0-9]+ [0-9]+ ([0-9]+)', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return response length as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_request_referrer(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract referrer URL (between response length and user agent)
        match = re.search(r'HTTP/[0-9]+\.[0-9]+ [0-9]+ [0-9]+ ([^\s]+)', input_entry)
        if match and match.group(1) != '-':
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return referrer as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_http_request_user_agent(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Extract user agent (last field, everything after the referrer)
        match = re.search(r'HTTP/[0-9]+\.[0-9]+ [0-9]+ [0-9]+ [^\s]+ (.+)$', input_entry)
        if match:
            return [match.group(1)]
        return []

    def transform(extracted_values: typing.List[str]) -> str:
        # Return user agent as-is
        if extracted_values:
            return extracted_values[0]
        return ''

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_class_uid(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Static value for HTTP Activity class_uid
        return ['4002']

    def transform(extracted_values: typing.List[str]) -> str:
        # Return static class_uid value
        return '4002'

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_category_uid(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Static value for Network Activity category_uid
        return ['4']

    def transform(extracted_values: typing.List[str]) -> str:
        # Return static category_uid value
        return '4'

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_type_uid(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Calculate type_uid based on HTTP method (class_uid * 100 + activity_id)
        match = re.search(r'\] (GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|CONNECT) ', input_entry)
        if match:
            method = match.group(1)
            # Map HTTP methods to activity_id values
            method_map = {
                'GET': 3,
                'POST': 6,
                'DELETE': 2,
                'HEAD': 4,
                'OPTIONS': 5,
                'PUT': 7,
                'TRACE': 8,
                'CONNECT': 1
            }
            activity_id = method_map.get(method, 99)
            type_uid = 4002 * 100 + activity_id
            return [str(type_uid)]
        return ['400200']  # Unknown

    def transform(extracted_values: typing.List[str]) -> str:
        # Return calculated type_uid
        if extracted_values:
            return extracted_values[0]
        return '400200'

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_severity_id(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Static value for informational severity
        return ['1']

    def transform(extracted_values: typing.List[str]) -> str:
        # Return static severity_id value
        return '1'

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def transformer_action_id(input_data: str) -> str:
    def extract(input_entry: str) -> typing.List[str]:
        # Static value for allowed action
        return ['1']

    def transform(extracted_values: typing.List[str]) -> str:
        # Return static action_id value
        return '1'

    extracted_data = extract(input_data)
    transformed_data = transform(extracted_data)
    return transformed_data

def set_path(d: typing.Dict[str, typing.Any], path: str, value: typing.Any) -> None:
    keys = path.split('.')
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value

def _convert_to_json_if_possible(value: str) -> typing.Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def transformer(input_data: str) -> typing.Dict[str, typing.Any]:
    output = {}

    transformer_src_endpoint_ip_result = transformer_src_endpoint_ip(input_data)
    transformer_src_endpoint_ip_result = _convert_to_json_if_possible(transformer_src_endpoint_ip_result)
    set_path(output, 'src_endpoint.ip', transformer_src_endpoint_ip_result)

    transformer_time_result = transformer_time(input_data)
    transformer_time_result = _convert_to_json_if_possible(transformer_time_result)
    set_path(output, 'time', transformer_time_result)

    transformer_http_request_http_method_result = transformer_http_request_http_method(input_data)
    transformer_http_request_http_method_result = _convert_to_json_if_possible(transformer_http_request_http_method_result)
    set_path(output, 'http_request.http_method', transformer_http_request_http_method_result)

    transformer_activity_id_result = transformer_activity_id(input_data)
    transformer_activity_id_result = _convert_to_json_if_possible(transformer_activity_id_result)
    set_path(output, 'activity_id', transformer_activity_id_result)

    transformer_http_request_url_url_string_result = transformer_http_request_url_url_string(input_data)
    transformer_http_request_url_url_string_result = _convert_to_json_if_possible(transformer_http_request_url_url_string_result)
    set_path(output, 'http_request.url.url_string', transformer_http_request_url_url_string_result)

    transformer_http_request_url_path_result = transformer_http_request_url_path(input_data)
    transformer_http_request_url_path_result = _convert_to_json_if_possible(transformer_http_request_url_path_result)
    set_path(output, 'http_request.url.path', transformer_http_request_url_path_result)

    transformer_http_request_url_query_string_result = transformer_http_request_url_query_string(input_data)
    transformer_http_request_url_query_string_result = _convert_to_json_if_possible(transformer_http_request_url_query_string_result)
    set_path(output, 'http_request.url.query_string', transformer_http_request_url_query_string_result)

    transformer_http_request_version_result = transformer_http_request_version(input_data)
    transformer_http_request_version_result = _convert_to_json_if_possible(transformer_http_request_version_result)
    set_path(output, 'http_request.version', transformer_http_request_version_result)

    transformer_http_response_code_result = transformer_http_response_code(input_data)
    transformer_http_response_code_result = _convert_to_json_if_possible(transformer_http_response_code_result)
    set_path(output, 'http_response.code', transformer_http_response_code_result)

    transformer_http_response_length_result = transformer_http_response_length(input_data)
    transformer_http_response_length_result = _convert_to_json_if_possible(transformer_http_response_length_result)
    set_path(output, 'http_response.length', transformer_http_response_length_result)

    transformer_http_request_referrer_result = transformer_http_request_referrer(input_data)
    transformer_http_request_referrer_result = _convert_to_json_if_possible(transformer_http_request_referrer_result)
    set_path(output, 'http_request.referrer', transformer_http_request_referrer_result)

    transformer_http_request_user_agent_result = transformer_http_request_user_agent(input_data)
    transformer_http_request_user_agent_result = _convert_to_json_if_possible(transformer_http_request_user_agent_result)
    set_path(output, 'http_request.user_agent', transformer_http_request_user_agent_result)

    transformer_class_uid_result = transformer_class_uid(input_data)
    transformer_class_uid_result = _convert_to_json_if_possible(transformer_class_uid_result)
    set_path(output, 'class_uid', transformer_class_uid_result)

    transformer_category_uid_result = transformer_category_uid(input_data)
    transformer_category_uid_result = _convert_to_json_if_possible(transformer_category_uid_result)
    set_path(output, 'category_uid', transformer_category_uid_result)

    transformer_type_uid_result = transformer_type_uid(input_data)
    transformer_type_uid_result = _convert_to_json_if_possible(transformer_type_uid_result)
    set_path(output, 'type_uid', transformer_type_uid_result)

    transformer_severity_id_result = transformer_severity_id(input_data)
    transformer_severity_id_result = _convert_to_json_if_possible(transformer_severity_id_result)
    set_path(output, 'severity_id', transformer_severity_id_result)

    transformer_action_id_result = transformer_action_id(input_data)
    transformer_action_id_result = _convert_to_json_if_possible(transformer_action_id_result)
    set_path(output, 'action_id', transformer_action_id_result)

    return output

