# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Dell, Inc. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Dell, Inc. BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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

class CIM_BIOSAttribute(CIM_ManagedElement):
    _property_list  = {"AttributeName": "string", "CurrentValue": "string", "PendingValue": "string", "IsOrderedList": "string", "IsReadOnly": "string", "DefaultValue": "string"}


class CIM_BIOSEnumeration(CIM_BIOSAttribute):
    _property_list  = {"PossibleValues":"string", "PossibleValuesDescription": "string"}
class CIM_BIOSString(CIM_BIOSAttribute):
    _property_list  = {"StringType": "uint32", "MinLength": "uint64", "MaxLength": "uint64", "ValueExpression": "string",}
class CIM_BIOSInteger(CIM_BIOSAttribute):
    _property_list  = {"LowerBound": "uint64", "UpperBound": "uint64", "ProgrammaticUnit": "string", "ScalarIncrement": "uint32"}


class CIM_Job(CIM_LogicalElement):
    _property_list  = {
        "JobStatus": 'string',
        "TimeSubmitted": 'datetime',
        'ScheduledStartTime': 'datetime',
        'StartTime': 'datetime',
        'ElapsedTime': 'datetime',
        'JobRunTimes': 'uint32',
        'RunMonth': 'uint8',
        'RunDay': 'sint8',
        'RunDayOfWeek': 'sint8',
        'RunStartInterval': 'datetime',
        'LocalOrUtcTime': 'uint16',
        'UntilTime': 'datetime',
        'Notify': 'string',
        "Owner": 'string',
        "Priority": 'uint32',
        "PercentComplete": 'uint16',
        "DeleteOnCompletion": 'boolean',
        "ErrorCode": 'uint16',
        "ErrorDescription": 'string',
        "RecoveryAction": 'uint16',
        "OtherRecoveryAction": 'string'}
    _methods = { "KillJob": {}, }

class CIM_ConcreteJob(CIM_Job):
    _property_list  = { "JobState": 'uint16', 'TimeOfLastStateChange': 'datetime', 'TimeBeforeRemoval': 'datetime', }
    _methods = { "RequestStateChange": {}, 'GetError': {} }