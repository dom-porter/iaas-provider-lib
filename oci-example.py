import logging
import logging.handlers
from time import gmtime

from iaas.client import client_factory
from iaas.enums import Providers
from iaas.exceptions import ProviderError, ClientException
from vm import VirtualMachine


def configure_logging() -> None:
    """
    Configures the logging

    :return: None
    """
    handler = logging.handlers.RotatingFileHandler(filename="oci-monitor.log",
                                                   maxBytes=20000,
                                                   backupCount=2,
                                                   encoding="utf-8")

    formatter = logging.Formatter(
        '%(asctime)s %(name)-15s [%(process)s] [%(thread)d] [%(levelname)s] %(message)s')
    formatter.converter = gmtime
    handler.setFormatter(formatter)

    # set the root logger level to info
    logging.basicConfig(handlers=[handler], level=logging.INFO)


def get_display_mame(vm: VirtualMachine) -> str:
    """
    Will return the display name if available otherwise it will return the vm_id

    :param vm: An instance of a VM
    :return: The name of the VM
    """
    if vm.display_name:
        return vm.display_name
    else:
        return vm.vm_id
    

def main() -> None:
    """
    Main function to call

    :return: None
    """
    logger = logging.getLogger("oci-monitor")
    try:
        client = client_factory(Providers.ORACLE)
        all_vms = client.get_all_vms()
        for vm in all_vms:

            if vm.state == "STOPPED":
                print(f"{get_display_mame(vm)} not running. Starting...")
                logger.error(f"{get_display_mame(vm)} not running. Starting...")

                client.start_vm(vm)
            else:
                print(f"{get_display_mame(vm)} -> {vm.state}")
                logger.debug(f"{get_display_mame(vm)} -> {vm.state}")
    except ClientException as ce:
        print(ce)
        logger.error(ce)
    except ProviderError as pe:
        print(pe)
        logger.error(pe)


if __name__ == '__main__':
    configure_logging()
    main()
