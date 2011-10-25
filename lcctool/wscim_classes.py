import wscim
import schemas
from stdcli.trace_decorator import traceLog, getLog

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

# eventually all these classes should be autogenerated from MOF files:
class CIM_ManagedElement(wscim.WSInstance):
    _property_list  = {"InstanceID": "string", "Caption": "string", "Description": "string", "ElementName": "string"}

class CIM_ManagedSystemElement(CIM_ManagedElement):
    _property_list  = {"InstallDate": 'datetime', 'Name': 'string', 'OperationalStatus': 'uint16', 'StatusDescriptions': 'string', 'Status': 'string', "HealthState": 'uint16', "CommunicationStatus": 'uint16', "DetailedStatus": 'uint16', 'OperatingStatus': 'uint16', "PrimaryStatus": 'uint16'}

class CIM_LogicalElement(CIM_ManagedSystemElement): pass

class CIM_EnabledLogicalElement(CIM_LogicalElement):
    _property_list  = {"EnabledState": 'uint16', "OtherEnabledState": 'string', "RequestedState": 'uint16', "EnabledDefault": 'uint16', "TimeOfLastStateChange": 'datetime', "AvailableRequestedStates": 'uint16', "TransitioningToState": 'uint16'}
    _methods = {"RequestStateChange": {}}

class CIM_Service(CIM_EnabledLogicalElement):
    _property_list  = {"SystemCreationClassName": 'string', "SystemName": 'string', "CreationClassName": "string", "PrimaryOwnerName": "string", "PrimaryOwnerContact": "string", "StartMode": "string", "Started": "boolean", }
    _methods = { "StartService": {}, "StopService": {} }

class CIM_BIOSService(CIM_Service):
    _methods = {
        "SetBIOSAttribute": {
            'input': {
                "TargetBIOS": "reference",
                "AttributeName": "string",
                "AttributeValue": "string",
                "AuthorizationToken": None,
                "PasswordEncoding": None
            },
            'output': {
                "SetResult": None,
                "ReturnValue": None,
            }
         },
        "SetBIOSAttributeEmbeddedInstance": {
            'input': {
                "TargetBIOS": "reference",
                "AttributeConfig": None,
                "AuthorizationToken": None,
                "PasswordEncoding": None
            },
            'output': {
                "SetResult": None,
                "ReturnValue": None,
            }
        },
        "ReadRawBIOSData": {
            'input': {
                "TargetBIOS": "reference",
                "Offset": "unsignedInt",
                "NumberOfBytes": "unsignedInt",
            },
            'output': {
                "NumberOfBytes": "unsignedInt",
                "Data": "unsignedByte",
                "ReturnValue": None,
            }
        },
        "WriteRawBIOSData": {
            'input': {
                "TargetBIOS": "reference",
                "Offset": "unsignedInt",
                "NumberOfBytes": "unsignedInt",
                "Data": "unsignedByte",
                "AuthorizationToken": None,
                "PasswordEncoding": None
            },
            'output': {
                "NumberOfBytes": "unsignedInt",
                "ReturnValue": None,
            }
        },
    }

# DELL SPECIFIC
class DCIM_BIOSService(CIM_Service):
    _ns = schemas.std_xml_namespaces['bios_srv']
    _methods = {
        "SetAttribute": {
            'input': {
                "Target": "string",
                "AttributeName": "string",
                "AttributeValue": "string",
            },
            'output': {
                "SetResult": "string",
                "RebootRequired": "string",
                "MessageID": "string",
                "Message": "string",
                "MessageArguments": "string",
            }
         },

        "SetAttributes": {
            'input': {
                "Target": "string",
                "AttributeName": "string",  # array
                "AttributeValue": "string",  # array
            },
            'output': {
                "SetResult": "string",  # array
                "RebootRequired": "string",  # array
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
        "CreateTargetedConfigJob": {
            'input': {
                "Target": "string",
                "RebootJobType": "uint16",
                "ScheduledStartTime": "string",  # array
                "UntilTime": "string",  # array
            },
            'output': {
                'Job': None,
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
        "DeletePendingConfiguration": {
            'input': {
                "Target": "string",
            },
            'output': {
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
        "ChangePassword": {
            'input': {
                "Target": "string",
                "PasswordType": "uint16",
                "OldPassword": "string",
                "NewPassword": "string",
            },
            'output': {
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
    }




class CIM_BIOSAttribute(CIM_ManagedElement):
    _property_list  = {"AttributeName": "string", "CurrentValue": "string", "PendingValue": "string", "IsOrderedList": "string", "IsReadOnly": "string", "DefaultValue": "string"}


class CIM_BIOSEnumeration(CIM_BIOSAttribute):
    _property_list  = {"PossibleValues":"string", "PossibleValuesDescription": "string"}
class CIM_BIOSString(CIM_BIOSAttribute):
    _property_list  = {"StringType": "uint32", "MinLength": "uint64", "MaxLength": "uint64", "ValueExpression": "string",}
class CIM_BIOSInteger(CIM_BIOSAttribute):
    _property_list  = {"LowerBound": "uint64", "UpperBound": "uint64", "ProgrammaticUnit": "string", "ScalarIncrement": "uint32"}

class DCIM_BIOSAttribute(CIM_BIOSAttribute, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_attr']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute'}
class DCIM_BIOSString(CIM_BIOSString, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_str']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute'}
class DCIM_BIOSinteger(CIM_BIOSInteger, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_int']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute'}
class DCIM_BIOSEnumeration(CIM_BIOSEnumeration, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_enum']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute'}

class DCIM_RAIDAttribute(CIM_BIOSAttribute, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['raid_attr']
class DCIM_RAIDString(CIM_BIOSString, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['raid_str']
class DCIM_RAIDInteger(CIM_BIOSInteger, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['raid_int']
class DCIM_RAIDEnumeration(CIM_BIOSEnumeration, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['raid_enum']

class DCIM_NICAttribute(CIM_BIOSAttribute, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['nic_attr']
class DCIM_NICString(CIM_BIOSString, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['nic_str']
class DCIM_NICInteger(CIM_BIOSInteger, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['nic_int']
class DCIM_NICEnumeration(CIM_BIOSEnumeration, wscim.DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['nic_enum']

class DCIM_iDRACCardAttribute(CIM_BIOSAttribute, wscim.DCIM_Mixin):
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_attr']
class DCIM_iDRACCardString(CIM_BIOSString, wscim.DCIM_Mixin):
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_str']
class DCIM_iDRACCardInteger(CIM_BIOSInteger, wscim.DCIM_Mixin):
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_int']
class DCIM_iDRACCardEnumeration(CIM_BIOSEnumeration, wscim.DCIM_Mixin):
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_enum']

