import flask
import classes.cosmosdbprocessor
import json
from flask import jsonify, request, abort
import netaddr


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


@app.before_first_request
def createprocessor():
    global cosmos_processor
    cosmos_processor = classes.cosmosdbprocessor.Processor()   # create a new Cosmos DB processor object


@app.route('/api/test', methods=['GET'])
def testapi():
    '''This is a test URI that can be used to confirm the service is operational'''
    return jsonify({"response": "Welcome to the Service Catalogue API"}), 200


@app.route('/api/vms/vm', methods=['GET', 'POST'])
def virtualmachines():
    '''This either retrieves all VMs or creates a new one'''

    if flask.request.method == 'GET':
        results = cosmos_processor.get_all_vms()

        # remove the system-defined properties (those that begin with "_")
        updated_results = []         # new list to hold all of the updated documents
        for document in results:
            updated_document = {}        # new dict to hold the results without the system defined properties
            for key in document.keys():
                if key[:1] != '_':   # checks to see if first character is "_"
                    updated_document[key] = document[key]
            updated_results.append(updated_document)

        return jsonify(updated_results), 200

    else:
        # They are making a post request so trying to create a new VM
        post_data = request.get_json()
        # note that if there isn't a header of content-type = "application/json" in the post request it will 
        # not be interpreted as json regardless of whether it is formatted as such
        
        if validate_new_vm(post_data):
            new_vmid = cosmos_processor.add_vm(post_data['name'], post_data['ipaddresses'])
            if not new_vmid:
                return abort(400)
            else:
                return jsonify(new_vmid), 201
        else:
            # the data being passed in has failed the validation so return a 400
            return abort(400)


@app.route('/api/vms/vm/<string:vmid>', methods=['DELETE'])
def delete_vm(vmid):
    '''This deletes a specific VM'''
    if cosmos_processor.delete_vm(vmid):
        return '', 204
    else:
        return '', 404


@app.route('/api/service-operations/restart-vm/<string:vmid>', methods=['POST'])
def restart_vm(vmid):
    '''This restarts a VM'''
    restart_vm = cosmos_processor.restart_vm(vmid)
    if restart_vm == 'success':
        return jsonify({"response": "Successfully restarted " + vmid}), 200
    elif restart_vm == 'off':
        return jsonify({"response": "Unable to restart " + vmid + ". Machine is turned off"}), 200
    else:
        return '', 404


@app.route('/api/network/firewall/rules/rule', methods=['GET', 'POST'])
def firewall_rules():
    '''This either gets all firewall rules or adds a new one'''
    if flask.request.method == 'GET':
        results = cosmos_processor.get_all_rules()

        # remove the system-defined properties (those that begin with "_")
        updated_results = []         # new list to hold all of the updated documents
        for document in results:
            updated_document = {}        # new dict to hold the results without the system defined properties
            for key in document.keys():
                if key[:1] != '_':   # checks to see if first character is "_"
                    updated_document[key] = document[key]
            updated_results.append(updated_document)

        return jsonify(updated_results), 200

    else:
        # this must be a POST request so want to create a new firewall rule
        post_data = request.get_json()
        # note that if there isn't a header of content-type = "application/json" in the post request it will 
        # not be interpreted as json regardless of whether it is formatted as such

        if validate_new_rule(post_data):
            print("passed rule validation")
            new_fwid = cosmos_processor.add_rule(post_data['name'], post_data['from'], post_data['to'], post_data['action'])
            return jsonify(new_fwid), 201
        else:
            # the data being passed in has failed the validation so return a 400
            return abort(400)


if __name__ == "__main__":
    app.run(port=8080)
