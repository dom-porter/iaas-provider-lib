from typing import Protocol, List, Optional

from clients.netcup import NetcupClient
from clients.oracle import OracleClient
from iaas.enums import Providers
from iaas.vm import VirtualMachine


class Client(Protocol):
    """ Used as an interface for all IaaS API clients """

    def get_all_vms(self) -> list[VirtualMachine]:
        ...

    def stop_vm(self, vm: VirtualMachine) -> str:
        ...

    def force_stop_vm(self, vm: VirtualMachine) -> str:
        ...

    def start_vm(self, vm: VirtualMachine) -> str:
        ...

    def restart_vm(self, vm: VirtualMachine) -> str:
        ...

    def get_public_ips(self, vm: VirtualMachine) -> List[str]:
        ...


FACTORIES = {
    Providers.ORACLE: OracleClient,
    Providers.NETCUP: NetcupClient
}


def client_factory(provider: Providers, config_path: Optional[str] = None) -> Client:
    """
    Creates an instance of an IaaS provider client. Factory does not maintain any of the instances it creates.

    Path is optional and by default will use the ./config/<client>.ini if no path is specified.

    :param provider: The required provider for the service you wish to use.
    :param config_path: (Optional) The alternate path to the config file.
    :return: Instance of iaas.client.Client
    """
    return FACTORIES[provider](config_path)
