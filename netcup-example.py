import logging
import logging.handlers
from time import gmtime

from iaas.exceptions import ClientException, ProviderError
from iaas.client import client_factory, Providers
from vm import VirtualMachine


def configure_logging() -> None:
    """
    Configures the logging

    :return: None
    """
    handler = logging.handlers.RotatingFileHandler(filename="netcup-monitor.log",
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
    logger = logging.getLogger("netcup-monitor")
    try:
        print("netcup-example")
        client = client_factory(Providers.NETCUP)
        vm_list = client.get_all_vms()
        for vm in vm_list:

            if vm.state.upper() == "STOPPED":
                print(f"{get_display_mame(vm)} not running. Starting...")
                logger.error(f"{get_display_mame(vm)} not running. Starting...")

                client.start_vm(vm)
            else:
                print(f"{get_display_mame(vm)} -> {vm.state}")
                logger.debug(f"{get_display_mame(vm)} -> {vm.state}")
    except ClientException as ce:
        print(ce.message)
        logger.error(ce.message)
    except ProviderError as pe:
        print(pe.message)
        logger.error(pe.message)


if __name__ == '__main__':
    configure_logging()
    main()
