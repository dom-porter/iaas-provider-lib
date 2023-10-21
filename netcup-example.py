import asyncio
import logging
import logging.handlers
from time import gmtime

from iaas import client as iaas_client
from iaas import exceptions as iaas_ex

logger = logging.getLogger("netcup-monitor")


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


def get_display_mame(vm: iaas_client.VirtualMachine) -> str:
    """
    Will return the display name if available otherwise it will return the vm_id

    :param vm: An instance of a VM
    :return: The name of the VM
    """
    if vm.display_name:
        return vm.display_name
    else:
        return vm.vm_id


async def monitor_vm(vm, client):
    if vm.state == "STOPPED":
        print(f"{get_display_mame(vm)} not running. Starting...")
        logger.error(f"{get_display_mame(vm)} not running. Starting...")

        await client.start_vm(vm)
    else:
        print(f"{get_display_mame(vm)} -> {vm.state}")
        logger.debug(f"{get_display_mame(vm)} -> {vm.state}")


async def main() -> None:
    """
    Main function to call

    :return: None
    """

    try:
        print("netcup-example")
        client = iaas_client.client_factory(iaas_client.Providers.NETCUP)
        all_vms = await client.get_all_vms()
        tasks = [asyncio.create_task(monitor_vm(vm, client)) for vm in all_vms]
        await asyncio.gather(*tasks)

    except iaas_ex.ClientException as ce:
        print(ce.message)
        logger.error(ce.message)
    except iaas_ex.ProviderError as pe:
        print(pe.message)
        logger.error(pe.message)


if __name__ == '__main__':
    configure_logging()
    asyncio.run(main())
