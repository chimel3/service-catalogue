import config_cosmos
import pydocumentdb.document_client as document_client
from netaddr import IPNetwork


# Create the connection to Cosmos DB
client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})

# Create the database
db = client.CreateDatabase({'id': config_cosmos.COSMOSDB_DATABASE})

# Create the collections
collection_vm = client.CreateCollection(db['_self'],{'id': config_cosmos.COSMOSDB_COLLECTION_VM})
collection_vmid = client.CreateCollection(db['_self'],{'id': config_cosmos.COSMOSDB_COLLECTION_VMID})
collection_ip = client.CreateCollection(db['_self'],{'id': config_cosmos.COSMOSDB_COLLECTION_IP})
collection_fw = client.CreateCollection(db['_self'],{'id': config_cosmos.COSMOSDB_COLLECTION_FW})
collection_fwid = client.CreateCollection(db['_self'],{'id': config_cosmos.COSMOSDB_COLLECTION_FWID})
collection_subnet = client.CreateCollection(db['_self'],{'id': config_cosmos.COSMOSDB_COLLECTION_SUBNET})

# Load the subnets into the subnet collection - 10.20.30.0/24 and 10.220.30.0/24
# Deciding to let ID be auto-created as / character in subnet prevents its use as an ID.
client.CreateDocument(collection_subnet['_self'],{'subnet': "10.20.30.0/24"})
client.CreateDocument(collection_subnet['_self'],{'subnet': "10.220.30.0/24"})

# Load the IP address ranges into the IP collection for the subnets defined
for ipaddress in IPNetwork('10.20.30.0/24'):
    if str(ipaddress) != '10.20.30.0' and str(ipaddress) != '10.20.30.255':
        client.CreateDocument(collection_ip['_self'],{'id': str(ipaddress), 'usedby': ""})

for ipaddress in IPNetwork('10.220.30.0/24'):
    if str(ipaddress) != '10.220.30.0' and str(ipaddress) != '10.220.30.255':
        client.CreateDocument(collection_ip['_self'],{'id': str(ipaddress), 'usedby': ""})

# Load the virtual machines and reserve their IP addresses in the IP collection
vm = client.CreateDocument(collection_vm['_self'],{
                                            'id': "vm-1",
                                            'name': "sylvester",
                                            'ip': ["10.20.30.48"],
                                            'state': "on"})

for each_ip in vm['ip']:
    document = next(doc for doc in client.ReadDocuments(collection_ip['_self']) if doc['id'] == each_ip)
    document_link = document['_self']
    document['usedby'] = vm['id']
    client.ReplaceDocument(document_link, document)

vm = client.CreateDocument(collection_vm['_self'],{
                                            'id': "vm-2",
                                            'name': "tom",
                                            'ip': ["10.20.30.17"],
                                            'state': "on"})

for each_ip in vm['ip']:
    document = next(doc for doc in client.ReadDocuments(collection_ip['_self']) if doc['id'] == each_ip)
    document_link = document['_self']
    document['usedby'] = vm['id']
    client.ReplaceDocument(document_link, document)

vm = client.CreateDocument(collection_vm['_self'],{
                                            'id': "vm-3",
                                            'name': "garfield",
                                            'ip': ["10.20.30.60", "10.220.30.60"],
                                            'state': "on"})

for each_ip in vm['ip']:
    document = next(doc for doc in client.ReadDocuments(collection_ip['_self']) if doc['id'] == each_ip)
    document_link = document['_self']
    document['usedby'] = vm['id']
    client.ReplaceDocument(document_link, document)

vm = client.CreateDocument(collection_vm['_self'],{
                                            'id': "vm-4",
                                            'name': "heathcliff",
                                            'ip': ["10.20.30.78"],
                                            'state': "off"})

for each_ip in vm['ip']:
    document = next(doc for doc in client.ReadDocuments(collection_ip['_self']) if doc['id'] == each_ip)
    document_link = document['_self']
    document['usedby'] = vm['id']
    client.ReplaceDocument(document_link, document)

# enter the next vmid in the vm-id collection. Note that vmids will not reused.
client.CreateDocument(collection_vmid['_self'],{'nextvmid': "vm-5"})

# load the firewall rules
fw = client.CreateDocument(collection_fw['_self'],{
                                            'id': "fw-1",
                                            'name': "internet to sylvester",
                                            'from': "0.0.0.0/0",
                                            'to': "vm-1",
                                            'action': "allow"})

fw = client.CreateDocument(collection_fw['_self'],{
                                            'id': "fw-2",
                                            'name': "to tom",
                                            'from': "10.20.30.40/29",
                                            'to': "vm-2",
                                            'action': "allow"})

fw = client.CreateDocument(collection_fw['_self'],{
                                            'id': "fw-3",
                                            'name': "management adapters to NTP source",
                                            'from': "10.220.30.0/24",
                                            'to': "10.220.32.18",
                                            'action': "allow"})

fw = client.CreateDocument(collection_fw['_self'],{
                                            'id': "fw-4",
                                            'name': "default rule",
                                            'from': "0.0.0.0/0",
                                            'to': "0.0.0.0/0",
                                            'action': "deny"})

# Update the fwid collection with the next fwid to be issued. These are not reused.
client.CreateDocument(collection_fwid['_self'],{'nextfwid': "fw-5"})
