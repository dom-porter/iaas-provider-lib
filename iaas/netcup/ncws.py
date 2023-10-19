import xml
import xml.etree.ElementTree as et
from typing import List
from xml.etree.ElementTree import tostring

import requests

from iaas.netcup.exceptions import ValidationException, ServiceException, NotAllowedException

"""
An implementation of a Netcup Webservice API client
    
More details
https://helpcenter.netcup.com/en/wiki/server/scp-webservice
https://www.servercontrolpanel.de/WSEndUser?wsdl
"""

API_URL = "https://www.servercontrolpanel.de:443/SCP/WSEndUser"
REQUEST_HEADERS = {'content-type': 'text/xml'}
ENVELOPE_ATTRIBUTES = {"xmlns:soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
                       "xmlns:end": "http://enduser.service.web.vcp.netcup.de/"}


def soap_message_factory(end_point: str, variables: dict[str, str]) -> xml.etree.ElementTree.Element:
    """
    Creates a SOAP request for the webservice.
    Does not maintain the result after creation.

    :param end_point: The webservice endpoint.
    :param variables: A dictionary of all the variables for the SOAP call.
    :return: xml.etree.ElementTree.Element
    """

    envelope = et.Element("soapenv:Envelope", ENVELOPE_ATTRIBUTES)
    header = et.SubElement(envelope, 'soapenv:Header')
    body = et.SubElement(envelope, 'soapenv:Body')
    api_end_point = et.SubElement(body, f"end:{end_point}")

    for field, data in variables.items():
        api_var = et.SubElement(api_end_point, field)
        api_var.text = data
    return envelope


def get_v_servers(login: str, password: str) -> List[str]:
    """
    Returns a list of virtual machine names.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :return: A list of server names.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}"}

    soap_message = soap_message_factory("getVServers", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    server_list = root.findall(".//return")

    return [element.text for element in server_list]


def get_v_server_nickname(login: str, password: str, vm_name: str) -> str:
    """
    Returns the nickname of the vm. So far has not worked during testing.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: VM nickname if available. An empty string if not available.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("getVServerNickname", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    nickname = root.find(".//return")

    if nickname is not None:
        return nickname.text
    else:
        return ""


def get_v_server_state(login: str, password: str, vm_name: str) -> str:
    """
    Returns the VM state.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: The state of the VM (online/offline) if available. An empty string if not available.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("getVServerState", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    state = root.find(".//return")
    if state is not None:
        return state.text
    else:
        return ""


def v_server_start(login: str, password: str, vm_name: str) -> str:
    """
    Starts the VM.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: Response from the webservice. True or false as a string not boolean.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("vServerStart", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    api_response = root.find(".//return")

    return api_response.text


def v_server_power_off(login: str, password: str, vm_name: str) -> str:
    """
    The Server will be shut down. Forced shutdown.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: Response from the webservice. True or false as a string not boolean.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("vServerPoweroff", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    api_response = root.find(".//return")

    return api_response.text


def v_server_acpi_shutdown(login: str, password: str, vm_name: str) -> str:
    """
    Sending an ACPI shutdown signal to operating system.
    If the signal will be accepted, the operating system will be shut down.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: Response from the webservice. True or false as a string not boolean.
    """

    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("vServerACPIShutdown", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    api_response = root.find(".//return")

    return api_response.text


def v_server_reset(login: str, password: str, vm_name: str) -> str:
    """
    The Server will be reset from outside. During this process it can lead to data loss.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: Response from the webservice. True or false as a string not boolean.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("vServerReset", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    api_response = root.find(".//return")

    return api_response.text


def v_server_acpi_reboot(login: str, password: str, vm_name: str) -> str:
    """
    Server is shutdown via ACPI and started after Server powered off.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: Response from the webservice. True or false as a string not boolean.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("vServerACPIReboot", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    api_response = root.find(".//return")

    return api_response.text


def get_v_server_ips(login: str, password: str, vm_name: str) -> List[str]:
    """
    Returns a list of IP addresses for the server. This is an assumption as test server only has a single IP.

    :param login: The account login name.
    :param password: The webservice password and not account password.
    :param vm_name: The VM name and not the nickname.
    :return: List of IPs.
    """
    var_dic = {"loginName": f"{login}",
               "password": f"{password}",
               "vserverName": f"{vm_name}"}

    soap_message = soap_message_factory("getVServerIPs", var_dic)
    response = requests.post(API_URL, data=tostring(soap_message), headers=REQUEST_HEADERS)

    check_for_error(response.text)
    root = et.fromstring(response.text)
    ip_list = root.findall(".//return")

    return [element.text for element in ip_list]


def check_for_error(soap_response: str) -> None:
    """
    Checks if the response from the webservice is an error.
    If it is then an exception is raised using the exception_factory method.

    :param soap_response: The response returned from the API call.
    :return: None.
    """
    root = et.fromstring(soap_response)
    fault_string = root.find(".//faultstring")
    if fault_string is not None:
        exception_factory(fault_string.text)


EXCEPTIONS = {"validation error": ValidationException,
              "action not allowed": NotAllowedException}


def exception_factory(fault_string: str) -> None:
    """
    Raises an exception from errors generated from the webservice.

    :param fault_string: The fault string returned from the API call.
    :return: Exception.
    """
    if EXCEPTIONS.get(fault_string):
        raise EXCEPTIONS.get(fault_string)(fault_string)
    else:
        raise ServiceException(f"Error processing request - {fault_string}")
