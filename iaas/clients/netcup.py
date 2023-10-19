import configparser
from typing import List, Optional

from iaas.enums import Providers
from iaas.exceptions import ClientException, ProviderError
from iaas.netcup import ncws
from iaas.netcup.exceptions import ValidationException, ServiceException
from iaas.vm import VirtualMachine


def set_config_path(path: Optional[str]) -> str:
    """
    Returns the path to the config file. If no path is specified it will use the default path.

    :param path: The full path to an optional config file
    :return: path: The evaluated path to the config file
    """
    if path:
        return path
    else:
        return "./config/netcup.ini"


class NetcupClient:
    """
    Netcup VPS client.
    Client uses bespoke Netcup SOAP API located in the iaas.netcup directory.
    """

    def __init__(self, path: Optional[str] = None):
        self._config_path = set_config_path(path)
        self._config = configparser.ConfigParser()
        self._config.read(self._config_path)

    def get_all_vms(self) -> list[VirtualMachine]:
        """
        Returns a list of VMs.

        :return: A list of iaas.vm.VirtualMachine
        """
        vm_list = []
        try:
            vm_id_list = ncws.get_v_servers(self._config.get("DEFAULT", "loginName"),
                                            self._config.get("DEFAULT", "password"))

            for vm_id in vm_id_list:
                display_name = ncws.get_v_server_nickname(self._config.get("DEFAULT", "loginName"),
                                                          self._config.get("DEFAULT", "password"),
                                                          vm_id)
                state = ncws.get_v_server_state(self._config.get("DEFAULT", "loginName"),
                                                self._config.get("DEFAULT", "password"),
                                                vm_id)
                vm = VirtualMachine(vm_id=vm_id, display_name=display_name, state=state, provider=Providers.NETCUP)
                vm_list.append(vm)

            return vm_list

        except ValidationException as ve:
            raise ClientException(
                f"Netcup API error getting VM list. Check that login details are correct - {ve.message}") from None
        except ValueError as vle:
            raise ClientException(
                f"Failed to create VM instance due to unknown state returned from Netcup API.") from None
        except ServiceException as se:
            raise ProviderError(f"Netcup API error returned when getting list of VMs - {se.message}") from None

    def stop_vm(self, vm: VirtualMachine) -> str:
        """
        Stops the supplied VM.

        :param vm: A virtual machine
        :return: The result from the webservice call
        """
        try:
            result = ncws.v_server_acpi_shutdown(self._config.get("DEFAULT", "loginName"),
                                                 self._config.get("DEFAULT", "password"),
                                                 vm.vm_id)
            return result
        except ServiceException as se:
            raise ProviderError(f"Error returned from Netcup API when stopping VM - {se.message}") from None
        except ValidationException as ve:
            raise ProviderError(
                f"Netcup API error stopping VM. Check that login details are correct - {ve.message}") from None

    def force_stop_vm(self, vm: VirtualMachine) -> str:
        """
        Force stop the supplied VM.

        :param vm: A virtual machine
        :return: The result from the webservice call
        """
        try:
            result = ncws.v_server_power_off(self._config.get("DEFAULT", "loginName"),
                                             self._config.get("DEFAULT", "password"),
                                             vm.vm_id)
            return result
        except ServiceException as se:
            raise ProviderError(f"Error returned from Netcup API when stopping VM - {se.message}") from None
        except ValidationException as ve:
            raise ProviderError(
                f"Netcup API error stopping VM. Check that login details are correct - {ve.message}") from None

    def start_vm(self, vm: VirtualMachine) -> str:
        """
        Starts the supplied VM.

        :param vm: A virtual machine.
        :return: The result from the webservice call.
        """
        try:
            result = ncws.v_server_start(self._config.get("DEFAULT", "loginName"),
                                         self._config.get("DEFAULT", "password"),
                                         vm.vm_id)
            return result
        except ServiceException as se:
            raise ProviderError(f"Error returned from Netcup API when starting VM - {se.message}") from None
        except ValidationException as ve:
            raise ProviderError(
                f"Netcup API error starting VM. Check that login details are correct - {ve.message}") from None

    def restart_vm(self, vm: VirtualMachine) -> str:
        """
        Restarts the supplied VM.

        :param vm: A virtual machine.
        :return: The result from the webservice call.
        """
        try:
            result = ncws.v_server_acpi_reboot(self._config.get("DEFAULT", "loginName"),
                                               self._config.get("DEFAULT", "password"),
                                               vm.vm_id)
            return result
        except ServiceException as se:
            raise ProviderError(f"Error returned from Netcup API when restarting VM - {se.message}") from None
        except ValidationException as ve:
            raise ProviderError(
                f"Netcup API error restarting VM. Check that login details are correct - {ve.message}") from None

    def get_public_ips(self, vm: VirtualMachine) -> List[str]:
        """
        Returns a list of IPs for the supplied VM.

        :param vm: A virtual machine.
        :return: A list of IPs.
        """
        try:
            ip_list = ncws.get_v_server_ips(self._config.get("DEFAULT", "loginName"),
                                            self._config.get("DEFAULT", "password"),
                                            vm.vm_id)
            return ip_list
        except ServiceException as se:
            raise ProviderError(f"Error returned from Netcup API when getting list of IPs - {se.message}") from None
        except ValidationException as ve:
            raise ProviderError(
                f"Netcup API error getting list of IPs. Check that login details are correct -{ve.message}") from None
