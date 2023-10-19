import logging
import logging.handlers
from time import gmtime

from iaas.exceptions import ClientException, ProviderError
from iaas.client import client_factory, Providers
from iaas.vm import VirtualMachine


def configure_logging() -> None:
    """
    Configures the logging

    :return: None
    """
    handler = logging.handlers.RotatingFileHandler(filename="mixed-monitor.log",
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
    logger = logging.getLogger("mixed-monitor")
    all_clients = {}
    try:
        print("mixed-example")
        all_clients[Providers.NETCUP] = client_factory(Providers.NETCUP)
        all_clients[Providers.ORACLE] = client_factory(Providers.ORACLE)
        vm_list = []
        for client in all_clients.values():
            vm_list.extend(client.get_all_vms())

        for vm in vm_list:

            if vm.state == "STOPPED":
                print(f"{get_display_mame(vm)} not running. Starting...")
                logger.error(f"{get_display_mame(vm)} not running. Starting...")

                all_clients[vm.provider].start_vm(vm)
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
