# Description

A small libray consisting of a client class that can get/manage virtual machines from multiple providers.</br></br>
Currently supports:</br>
Oracle Cloud Infrastructure</br>
Netcup

# Using the library

````
from iaas.exceptions import ClientException, ProviderError
from iaas.client import client_factory, Providers

client = client_factory(Providers.NETCUP)
vm_list = client.get_all_vms()

for vm in vm_list:
    print(vm.vm_id)
````

# Configuration
By default all configuration for the providers are stored in the ./config directory. If you wish to provide an alternate path, this can be done by adding the path when creating the client.

````
client = client_factory(Providers.NETCUP, "./mypath/netcup.ini")
````

# Virtual Machine States
As providers may have different names for the current state of the VM the library will change them to either RUNNING or STOPPED.

# Examples
Provided are three examples which will list the virtual machines and check the state. If the VM is not running, it will be started.:</br></br>
oci-example.py</br>
netcup-example.py</br>
mixed-example.py</br>




## License
Apache License Version 2.0