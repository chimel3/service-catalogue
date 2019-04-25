import config_cosmos
import pydocumentdb.document_client as document_client
from netaddr import IPNetwork

class Processor():
    '''Creates an object to perform all of the interactions with Cosmos DB'''
    client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})
    
    def __init__(self):
        db_link = 'dbs/' + config_cosmos.COSMOSDB_DATABASE
        db = self.client.ReadDatabase(db_link)

        collection_vm_link = db_link + '/colls/' + config_cosmos.COSMOSDB_COLLECTION_VM
        self.collection_vm = self.client.ReadCollection(collection_vm_link)

        collection_vmid_link = db_link + '/colls/' + config_cosmos.COSMOSDB_COLLECTION_VMID
        self.collection_vmid = self.client.ReadCollection(collection_vmid_link)

        collection_subnet_link = db_link + '/colls/' + config_cosmos.COSMOSDB_COLLECTION_SUBNET
        self.collection_subnet = self.client.ReadCollection(collection_subnet_link)

        collection_ip_link = db_link + '/colls/' + config_cosmos.COSMOSDB_COLLECTION_IP
        self.collection_ip = self.client.ReadCollection(collection_ip_link)

        collection_fw_link = db_link + '/colls/' + config_cosmos.COSMOSDB_COLLECTION_FW
        self.collection_fw = self.client.ReadCollection(collection_fw_link)

        collection_fwid_link = db_link + '/colls/' + config_cosmos.COSMOSDB_COLLECTION_FWID
        self.collection_fwid = self.client.ReadCollection(collection_fwid_link)


    def get_all_vms(self):
        '''Returns all VMs from the collection'''
        query = {'query': 'SELECT * FROM ' + config_cosmos.COSMOSDB_COLLECTION_VM}
        docs = self.client.QueryDocuments(self.collection_vm['_self'], query)
        return list(docs)  # must cast it to a list before it is readable as a list of records


    def add_vm(self, name, subnets):
        '''Adds a new document to the virtualmachines collection'''
        # Get the next vmid
        vmid_document = next(doc for doc in self.client.ReadDocuments(self.collection_vmid['_self']))
        next_vmid = int(vmid_document['nextvmid'][3:])  # grab just the numeric part of the ID as an integer

        # Confirm that the subnets provided are available in the database and get next available address if so
        ipaddresses = list()
        for subnet in subnets:
            # check whether the subnet is in the database. Return default of False if not found to avoid a StopIteration error
            if next((doc for doc in self.client.ReadDocuments(self.collection_subnet['_self']) if doc['subnet'] == subnet), False):
                # it is so get the first available IP address
                #ipaddresses.append(next(doc['id'] for doc in self.client.ReadDocuments(self.collection_ip['_self']) if doc['usedby'] == "" if '10.220.30.' in doc['id']))
                # Get the list of IP addresses that are in this subnet
                IPs_in_subnet = list()
                for ipaddress in IPNetwork(subnet):
                    IPs_in_subnet.append(str(ipaddress))

                # Strip out the first and last address in the range as these are not usable
                IPs_in_subnet = IPs_in_subnet[1:-1]

                # Get the next available IP address from the database
                ipaddresses.append(next(doc['id'] for doc in self.client.ReadDocuments(self.collection_ip['_self']) if doc['usedby'] == "" if doc['id'] in IPs_in_subnet))
            else:
                return False

        # Update vmid collection
        vmid_document['nextvmid'] = "vm-" + str(next_vmid + 1)
        new_vmid = self.client.ReplaceDocument(vmid_document['_self'], vmid_document)

        # Update ipaddress collection so that correct documents are registered against this new vmid
        for ipaddress in ipaddresses:
            ipaddress_document = next(doc for doc in self.client.ReadDocuments(self.collection_ip['_self']) if doc['id'] == ipaddress)
            ipaddress_document['usedby'] = "vm-" + str(next_vmid)
            new_ipaddress_reserved = self.client.ReplaceDocument(ipaddress_document['_self'], ipaddress_document)

        # Create new virtualmachines document
        new_vm = self.client.CreateDocument(self.collection_vm['_self'],{
                                                                'id': "vm-" + str(next_vmid),
                                                                'name': name,
                                                                'ip': ipaddresses,
                                                                'state': "off"})
        return new_vm['id']


    def delete_vm(self, vm_id):
        '''Deletes a VM from the database'''
        vm_to_delete = next((doc for doc in self.client.ReadDocuments(self.collection_vm['_self']) if doc['id'] == vm_id), None)
        if vm_to_delete is not None:
            # Free up any IP addresses it holds
            documents = [doc for doc in self.client.ReadDocuments(self.collection_ip['_self']) if doc['usedby'] == vm_to_delete['id']]
            for document in documents:
                document['usedby'] = ""
                replaced_document = self.client.ReplaceDocument(document['_self'], document)

            self.client.DeleteDocument(vm_to_delete['_self'])

            return True
        else:
            return False


    def restart_vm(self, vm_id):
        '''Restart a VM'''
        vm_to_restart = next((doc for doc in self.client.ReadDocuments(self.collection_vm['_self']) if doc['id'] == vm_id), None)
        if vm_to_restart is not None:
            if vm_to_restart['state'] == "on":
                return 'success'
            else:
                return 'off'
        else:
            return 'notfound'

    
    def get_all_rules(self):
        '''Retrieve all of the firewall rules'''
        query = {'query': 'SELECT * FROM ' + config_cosmos.COSMOSDB_COLLECTION_FW}
        docs = self.client.QueryDocuments(self.collection_fw['_self'], query)
        return list(docs)  # must cast it to a list before it is readable as a list of records


    def add_rule(self, name, destination, target, action):
        '''Adds a new document to the firewallrules collection'''
        # Get the next fwid
        fwid_document = next(doc for doc in self.client.ReadDocuments(self.collection_fwid['_self']))
        next_fwid = int(fwid_document['nextfwid'][3:])  # grab just the numeric part of the ID as an integer
        
        # Update fwid collection
        fwid_document['nextfwid'] = "fw-" + str(next_fwid + 1)
        new_fwid = self.client.ReplaceDocument(fwid_document['_self'], fwid_document)

        # Create new firewallrules document
        new_fw = self.client.CreateDocument(self.collection_fw['_self'],{
                                                                'id': "fw-" + str(next_fwid),
                                                                'name': name,
                                                                'from': destination,
                                                                'to': target,
                                                                'action': action})

        return new_fw['id']
