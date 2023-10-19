from dataclasses import dataclass

from iaas.enums import Providers

"""
As providers will all have different names for the VM states.
The VM_STATES dict will ensure a consistent naming convention for all VM providers.

The two states used will be RUNNING and STOPPED.
"""
VM_STATES = {"RUNNING": "RUNNING",  # Oracle Cloud
             "STOPPED": "STOPPED",  # Oracle Cloud
             "online": "RUNNING",   # NetCup
             "offline": "STOPPED",  # NetCup
             "": "UNKNOWN"}


@dataclass
class VirtualMachine:
    """ Basic information about the VM """

    display_name: str
    vm_id: str
    state: str
    provider: Providers

    def __init__(self, display_name: str, vm_id: str, state: str, provider: Providers):
        self.vm_id = vm_id
        self.display_name = display_name
        self.provider = provider
        self.set_state(state)

    def set_state(self, state: str) -> None:
        if VM_STATES.get(state):
            self.state = VM_STATES.get(state)
        else:
            raise ValueError from None
