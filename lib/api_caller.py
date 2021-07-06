import logging
import requests
import json

from . import constants as c


def api_call_post(endpoint: str, payload: dict, user_agent: str=c.DEFAULT_USER_AGENT, host: str=c.HOST):
    endpoint = endpoint if endpoint.startswith('http') else host + endpoint

    logging.info('POST - Connecting to endpoint %s', endpoint)
    logging.info('Using payload: %s', payload)

    r = requests.post(
        endpoint,
        json=payload,
        headers= None if user_agent is None else {'User-Agent' : user_agent}
    )

    try:
        result = r.json()
    except json.decoder.JSONDecodeError:
        result = {}

    if r.ok:
        logging.info('Response returned %s', r.status_code)
        logging.debug('Response JSON: %s', result)
    else:
        logging.warning('Response not OK (%s)', r.status_code)
        logging.warning('Payload: %s', payload)

    return {
        'http-code' : r.status_code,
        'data' : result
    }


def api_call_get(endpoint: str, payload: dict, user_agent: str=c.DEFAULT_USER_AGENT, host: str=c.HOST):
    endpoint = endpoint if endpoint.startswith('http') else host + endpoint

    logging.info('GET - Connecting to endpoint %s', endpoint)
    logging.info('Using payload: %s', payload)

    r = requests.get(
        endpoint,
        params=payload,
        headers= None if user_agent is None else {'User-Agent' : user_agent}
    )

    try:
        result = r.json()
    except json.decoder.JSONDecodeError:
        result = {}

    if r.ok:
        logging.info('Response returned %s', r.status_code)
        logging.debug('Response JSON: %s', result)
    else:
        logging.warning('Response not OK (%s)', r.status_code)
        logging.warning('Payload: %s', payload)

    return {
        'http-code' : r.status_code,
        'data' : result
    }
