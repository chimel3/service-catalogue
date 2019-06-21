'''
The main-stub script allows instantiation of this program but in a self-contained way that does not
require a database back-end in order to respond to requests as these operations are stubbed out.
This allows it to reply to the same calls as the proper program, but with fixed data sets
'''

import flask
# import classes.cosmosdbprocessor
import json
from flask import jsonify, request, abort
import netaddr
import random


app = flask.Flask(__name__)

def is_valid_subnet(subnet):
    try:
        netaddr.IPNetwork(subnet)
        return True
    except (netaddr.core.AddrFormatError, ValueError):
        return False


def validate_new_vm(parms):
    '''Does some  validation of the parameters being passed in'''

    if all (elements in parms for elements in ("name", "ipaddresses")):  # checks that there is a "name" and "ipaddresses" key
        if isinstance(parms["ipaddresses"], list):   # checks that it's a list even if a single IP
            # check format of IP subnets to ensure correct        
            for subnet in parms["ipaddresses"]:
                if is_valid_subnet(subnet):
                    return True
                else:
                    return False
        else:
            return False
    else:
        return False


def is_valid_vmid_format(vmid):
    '''Checks to see whether the argument passed in conforms to vmid format.
    Note that this does not confirm that the VMID exists'''
    if len(vmid.split("-")) != 2:
        return False
    if vmid.split("-")[0] != "vm":
        return False
    try:
        int(vmid.split("-")[1])
    except ValueError:
        return False

    # if get this far then passed the format tests so it looks like a VMID
    return True


def validate_new_rule(parms):
    '''Basic validation of the arguments being passed in.
    Consequently it will catch blatant errors in arguments but more subtle ones will be missed and
    can generate an error in the code'''
    
    if all (elements in parms for elements in ("name", "from", "to", "action")):  # confirms that the 4 required arguments exist in the parms blob
        # check to see if the "from" and "to" are either IPs, subnets or vmids
        if not netaddr.valid_ipv4(parms["from"]):
            if not is_valid_subnet(parms["from"]):
                # not a valid IP or subnet so check for valid vmid
                if not is_valid_vmid_format(parms["from"]):
                    return False

        if not netaddr.valid_ipv4(parms["to"]):
            if not is_valid_subnet(parms["to"]):
                # not a valid IP or subnet so check for valid vmid
                if not is_valid_vmid_format(parms["to"]):
                    return False

        if parms["action"] != 'allow' and parms["action"] != 'deny':
            return False

        return True
    else:
        return False


@app.route('/api/test', methods=['GET'])
def testapi():
    '''This is a test URI that can be used to confirm the service is operational'''
    return jsonify({"response": "Welcome to the Service Catalogue API"}), 200


@app.route('/api/vms/vm', methods=['GET', 'POST'])
def virtualmachines():
    '''This either retrieves all VMs or creates a new one'''

    if flask.request.method == 'GET':
        results = open("./stub/get_all_vms.json", 'r')
        updated_results = results.read()

        return jsonify(updated_results), 200

    else:
        # They are making a post request so trying to create a new VM
        post_data = request.get_json()
        # note that if there isn't a header of content-type = "application/json" in the post request it will 
        # not be interpreted as json regardless of whether it is formatted as such
        
        if validate_new_vm(post_data):
            return jsonify('{\'vmid\': \'vm-3000\'}'), 201
        else:
            # the data being passed in has failed the validation so return a 400
            return abort(400)


@app.route('/api/vms/vm/<string:vmid>', methods=['DELETE'])
def delete_vm(vmid):
    '''This deletes a specific VM'''
    # assume success here
    return '', 204


@app.route('/api/service-operations/restart-vm/<string:vmid>', methods=['POST'])
def restart_vm(vmid):
    '''This restarts a VM'''
    # make response random
    random_response = random.randrange(1,4)
    if random_response == 1:
        return jsonify({"response": "Successfully restarted " + vmid}), 200
    elif random_response == 2:
        return jsonify({"response": "Unable to restart " + vmid + ". Machine is turned off"}), 200
    else:
        return '', 404


@app.route('/api/network/firewall/rules/rule', methods=['GET', 'POST'])
def firewall_rules():
    '''This either gets all firewall rules or adds a new one'''
    if flask.request.method == 'GET':
        results = open("./stub/get_all_rules.json", 'r')
        updated_results = results.read()

        return jsonify(updated_results), 200

    else:
        # this must be a POST request so want to create a new firewall rule
        post_data = request.get_json()
        # note that if there isn't a header of content-type = "application/json" in the post request it will 
        # not be interpreted as json regardless of whether it is formatted as such

        if validate_new_rule(post_data):
            return jsonify('{\'fwid\': \'fw-5000\'}'), 201
        else:
            # the data being passed in has failed the validation so return a 400
            return abort(400)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)   # ensures that it doesn't just bind on 127.0.0.1 which is the default
