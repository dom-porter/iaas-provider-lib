from typing import List, Optional

import oci
from oci.core import ComputeClient, VirtualNetworkClient
from oci.core.models import instance
from oci.exceptions import InvalidConfig, ConfigFileNotFound, InvalidKeyFilePath, ServiceError

from iaas.enums import Providers
from iaas import exceptions as iaas_ex
from vm import VirtualMachine


def set_config_path(path: Optional[str]) -> str:
    """
    Returns the path to the config file. If no path is specified it will use the default path.

    :param path: (Optional) The full path to a config file
    :return: path: The evaluated path to the config file
    """
    if path:
        return path
    else:
        return "./config/oracle.ini"


def oracle_vm_factory(vm: instance) -> VirtualMachine:
    """
    Creates an instance of VirtualMachine class.
    Factory does not maintain any of the instances it creates.

    :param vm: oci.core.models.instance
    :return: iaas.vm.VirtualMachine
    """
    return VirtualMachine(
        display_name=vm.display_name,
        vm_id=vm.id,
        state=vm.lifecycle_state,
        provider=Providers.ORACLE
    )


class OracleClient:
    """
    Oracle Cloud client.

    More details:
    https://github.com/oracle/oci-python-sdk
    https://docs.oracle.com/en-us/iaas/tools/python/2.112.3/index.html

    """

    def __init__(self, path: Optional[str] = None):
        try:
            self._config_path = set_config_path(path)
            self._config = oci.config.from_file(file_location=self._config_path)
            oci.config.validate_config(self._config)
            self._compute_client = ComputeClient(self._config)
        except InvalidConfig as v:
            raise iaas_ex.ClientException(f"Config in {self._config_path} is not valid") from None
        except ConfigFileNotFound as c:
            raise iaas_ex.ClientException(f"Unable to locate config file {self._config_path}") from None
        except InvalidKeyFilePath as k:
            raise iaas_ex.ClientException(f"Unable to locate .pem file specified in {self._config_path}") from None

    async def get_all_vms(self) -> list[VirtualMachine]:
        """
        Returns a list of VirtualMachine class instances.

        :return: A list of iaas.vm.VirtualMachine
        """
        try:
            vm_instances = self._compute_client.list_instances(compartment_id=self._config["tenancy"]).data
            return [oracle_vm_factory(vm) for vm in vm_instances]
        except ServiceError as e:
            raise iaas_ex.ProviderError(
                f"Oracle API return an error when fetching list of VMs - {e.message}") from None

    async def stop_vm(self, vm: VirtualMachine) -> str:
        """
        Gracefully shuts down the instance by sending a shutdown command to the operating system.

        :param vm: A virtual machine.
        :return: The vm state.
        """

        vm_instance = self._compute_client.instance_action(vm.vm_id, action="SOFTSTOP")
        return vm_instance.data.lifecycle_state

    async def force_stop_vm(self, vm: VirtualMachine) -> str:
        """
        Power off the VM instance.

        :param vm: A virtual machine.
        :return: The vm state.
        """

        vm_instance = self._compute_client.instance_action(vm.vm_id, action="STOP")
        return vm_instance.data.lifecycle_state

    async def start_vm(self, vm: VirtualMachine) -> str:
        """
        Starts the supplied VM instance.

        :param vm: A virtual machine.
        :return: The vm state.
        """

        vm_instance = self._compute_client.instance_action(vm.vm_id, action="START")
        return vm_instance.data.lifecycle_state

    async def restart_vm(self, vm: VirtualMachine) -> str:
        """
        Restarts the supplied VM instance.

        :param vm: A virtual machine.
        :return: The vm state.
        """

        vm_instance = self._compute_client.instance_action(vm.vm_id, action="SOFTRESET")
        return vm_instance.data.lifecycle_state

    async def get_public_ips(self, vm: VirtualMachine) -> List[str]:
        """
        Returns a list of all public IP addresses assigned to the VM instance.

        :param vm: A virtual machine.
        :return: A list of IPs.
        """

        virtual_network_client = VirtualNetworkClient(self._config)

        vnic_attachments = self._compute_client.list_vnic_attachments(
            compartment_id=self._config["tenancy"],
            instance_id=vm.vm_id
        ).data

        # get a list of vNICs from the vNIC attachment. Possible to have multiple.
        vnics = [virtual_network_client.get_vnic(va.vnic_id).data for va in vnic_attachments]
        return [vnic.public_ip for vnic in vnics if vnic.public_ip]
