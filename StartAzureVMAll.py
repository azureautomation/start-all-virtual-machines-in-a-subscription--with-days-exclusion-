"""
Azure Automation documentation : https://aka.ms/azure-automation-python-documentation
Azure Python SDK documentation : https://aka.ms/azure-python-sdk
"""

import sys
import datetime

now = datetime.datetime.now()

day = now.strftime("%A")

if (day == "Saturday"):        
        print("Nothing to do") 
        sys.exit(0)
elif (day == "Sunday"):
        print("Nothing to do") 
        sys.exit(0)     
else:

    print("Start Virtual Machines - Process")

import os
import azure.mgmt.compute
from azure.mgmt.compute import ComputeManagementClient
import azure.mgmt.storage
import azure.mgmt.resource
import automationassets

def get_automation_runas_credential(runas_connection):
    from OpenSSL import crypto
    import binascii
    from msrestazure import azure_active_directory
    import adal

    # Get the Azure Automation RunAs service principal certificate
    cert = automationassets.get_automation_certificate("AzureRunAsCertificate")
    pks12_cert = crypto.load_pkcs12(cert)
    pem_pkey = crypto.dump_privatekey(crypto.FILETYPE_PEM,pks12_cert.get_privatekey())

    # Get run as connection information for the Azure Automation service principal
    application_id = runas_connection["ApplicationId"]
    thumbprint = runas_connection["CertificateThumbprint"]
    tenant_id = runas_connection["TenantId"]

    # Authenticate with service principal certificate
    resource ="https://management.core.windows.net/"
    authority_url = ("https://login.microsoftonline.com/"+tenant_id)
    context = adal.AuthenticationContext(authority_url)
    return azure_active_directory.AdalAuthentication(
    lambda: context.acquire_token_with_client_certificate(
            resource,
            application_id,
            pem_pkey,
            thumbprint)
    )

# Authenticate to Azure using the Azure Automation RunAs service principal
runas_connection = automationassets.get_automation_connection("AzureRunAsConnection")
azure_credential = get_automation_runas_credential(runas_connection)

# Initialize the compute management client with the RunAs credential and specify the subscription to work against.
resource_client = azure.mgmt.resource.ResourceManagementClient(
azure_credential,
  str(runas_connection["SubscriptionId"])
)
compute_client = ComputeManagementClient(
azure_credential,
  str(runas_connection["SubscriptionId"])
)

# Managing resource groups by location (change location as needed)
resource_group_params = 'westeurope'

# Get list of resource groups in the subscription
groups = []
groups = resource_client.resource_groups.list()
for group in groups:
    print ('Resource group: '+ group.name + ' Location: '+ group.location) 

# Get list of Virtual Machines for all the resource groups
    if (group.location == resource_group_params):
        vms = []
        vms = compute_client.virtual_machines.list(group.name)
        for vm in vms:
            print('VM name: '+ vm.name)
            vmd = compute_client.virtual_machines.get(group.name, vm.name, expand='instanceView')
            if vmd.instance_view.statuses[1].code == 'PowerState/deallocated':
                async_vm_start = compute_client.virtual_machines.start(group.name, vm.name)
                async_vm_start.wait()
                print("The Virtual Machine has been started")
    else:
        print("Nothing to do")
"""
Free script from Siren Solutions
http://sirensolutions.eu
"""
