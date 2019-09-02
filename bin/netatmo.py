import sys
import xml.dom.minidom, xml.sax.saxutils
import json
import logging
import os
import md5
import requests
import base64
import app_config

SCHEME = """<scheme>
    <title>Netatmo</title>
    <description>TODO</description>
    <use_external_validation>true</use_external_validation>
    <streaming_mode>simple</streaming_mode>
    <endpoint>
        <args>
            <arg name="name">
                <title>Name</title>
                <description>Unique identifier for this Modular Input instance .</description>
            </arg>
            <arg name="username">
                <title>Username</title>
                <description>TODO</description>
            </arg>
            <arg name="password">
                <title>Password</title>
                <description>TODO</description>
            </arg>
        </args>
    </endpoint>
</scheme>
"""

#<arg name="client_id">
#    <title>Client ID</title>
#    <description>TODO</description>
#</arg>
#<arg name="client_secret">
#    <title>Client Secret</title>
#    <description>TODO</description>
#</arg>

def do_scheme():
    print SCHEME


def validate_arguments():
    val_data = get_validation_data()

    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    data = {
        'grant_type': 'password',
        'username': val_data['username'],
        'password': val_data['password'],
        'client_id': app_config.client_id,
        'client_secret': app_config.client_secret,
        'scope': 'read_station read_thermostat'
    }
    url = 'https://api.netatmo.com/oauth2/token'
    response = requests.post(url, headers=headers, data=data)
    data = response.json()
    refresh_token = data['refresh_token']
    access_token = data['access_token']

    file_path = get_encoded_file_path(val_data['checkpoint_dir'], val_data['username'], "token")
    with open(file_path, 'w+') as f:
        f.write(str(refresh_token))
    f.close()
    pass


# Routine to index data
def run_script(): 

    config = get_config()

    client_id = app_config.client_id
    client_secret = app_config.client_secret

    refresh_token = read_refresh_token(config)

    refresh_headers = {'Host': 'https://api.netatmo.com/oauth2/token', 'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}
    refresh_data = {
        'Host': 'https://api.netatmo.com/oauth2/token',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token, 
        'client_id': client_id,
        'client_secret': client_secret
    }
    refresh_url = 'https://api.netatmo.com/oauth2/token'
    refresh_response = requests.post(refresh_url, data=refresh_data)
    
    refresh_data = refresh_response.json()
    access_token = refresh_data['access_token']

    params = {
        'access_token': access_token
    }

    try:
        response = requests.post("https://api.netatmo.com/api/getstationsdata", params=params)
        response.raise_for_status()
        data = response.json()["body"]["devices"][0]
    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)

    print(json.dumps(data, sort_keys=True))


def validate_conf(config, name): 
    # TODO
    pass


def get_config():
    config = {}

    try:
        # read everything from stdin
        config_str = sys.stdin.read()

        # parse the config XML
        doc = xml.dom.minidom.parseString(config_str)
        root = doc.documentElement
        conf_node = root.getElementsByTagName("configuration")[0]
        if conf_node:
            stanza = conf_node.getElementsByTagName("stanza")[0]
            if stanza:
                stanza_name = stanza.getAttribute("name")
                if stanza_name:
                    params = stanza.getElementsByTagName("param")
                    for param in params:
                        param_name = param.getAttribute("name")
                        if param_name and param.firstChild and \
                           param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                            data = param.firstChild.data
                            config[param_name] = data
                            #logging.debug("XML: '%s' -> '%s'" % (param_name, data))

        checkpnt_node = root.getElementsByTagName("checkpoint_dir")[0]
        if checkpnt_node and checkpnt_node.firstChild and \
           checkpnt_node.firstChild.nodeType == checkpnt_node.firstChild.TEXT_NODE:
            config["checkpoint_dir"] = checkpnt_node.firstChild.data

        if not config:
            raise Exception, "Invalid configuration received from Splunk."

        # just some validation: make sure these keys are present (required)
        validate_conf(config, "client_id")
        validate_conf(config, "client_secret")
        validate_conf(config, "redirect_uri")
        validate_conf(config, "code")
        validate_conf(config, "checkpoint_dir")

    except Exception, e:
        raise Exception, "Error getting Splunk configuration via STDIN: %s" % str(e)

    return config


def get_validation_data():
    val_data = {}

    # read everything from stdin
    val_str = sys.stdin.read()

    # parse the validation XML
    doc = xml.dom.minidom.parseString(val_str)
    root = doc.documentElement

    logging.debug("XML: found items")
    item_node = root.getElementsByTagName("item")[0]
    if item_node:
        logging.debug("XML: found item")

        name = item_node.getAttribute("name")
        val_data["stanza"] = name

        params_node = item_node.getElementsByTagName("param")
        for param in params_node:
            name = param.getAttribute("name")
            logging.debug("Found param %s" % name)
            if name and param.firstChild and \
               param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                val_data[name] = param.firstChild.data

        checkpnt_node = root.getElementsByTagName("checkpoint_dir")[0]
        if checkpnt_node and checkpnt_node.firstChild and \
          checkpnt_node.firstChild.nodeType == checkpnt_node.firstChild.TEXT_NODE:
            val_data["checkpoint_dir"] = checkpnt_node.firstChild.data

    return val_data


def get_encoded_file_path(checkpoint_dir, username, filetype):
    identifier = filetype+"_"+username
    return os.path.join(checkpoint_dir, identifier)


def save_checkpoint(config, filetype, value):
    chk_file = get_encoded_file_path(config["checkpoint_dir"], config['username'], filetype)
    with open(chk_file, 'w+') as f:
        f.write(str(value))
    f.close()


def read_checkpoint(config):
    chk_file = get_encoded_file_path(config["checkpoint_dir"], config['username'], "after")
    if (os.path.exists(chk_file)):
        with open(chk_file, 'r') as f:
            after = str(f.read())
        f.close()
        return after
    else:
        return None


def read_refresh_token(config):
    chk_file = get_encoded_file_path(config["checkpoint_dir"], config['username'], "token")
    refresh_token = None
    if (os.path.exists(chk_file)):
        with open(chk_file, 'r') as f:
            refresh_token = f.read()
        f.close()
    return refresh_token


# Script must implement these args: scheme, validate-arguments
if __name__ == '__main__':
    script_dirpath = os.path.dirname(os.path.join(os.getcwd(), __file__))

    if len(sys.argv) > 1:
        if sys.argv[1] == "--scheme":
            do_scheme()
        elif sys.argv[1] == "--validate-arguments":
            validate_arguments()
        else:
            pass
    else:
        run_script()

    sys.exit(0)