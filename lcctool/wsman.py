#!/usr/bin/python
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
#

import os
import re
import sys
import copy
import xml.dom.minidom
import ConfigParser

from stdcli.trace_decorator import traceLog, getLog
from stdcli.pycompat import call_output

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

basic_wsman_cmd = ["wsman", "enumerate", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]

unit_test_mode = False
test_data_dir = ""

dell_uri_list = {
    "bios":  [ "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration",
        "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString",
        "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger",],
    'nic': ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICAttribute"],
    'idrac': ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardAttribute"],
    }

order_files = {
    'bios': "BIOS0.01.xml",
    'idrac':"IDRAC0.01.xml",
    'nic':  "NIC0.01.xml",
    }

@traceLog()
def wsman_factory(*args, **kargs):
    if not unit_test_mode:
        return Wsman(*args, **kargs)
    else:
        return MockWsman(*args, **kargs)

class Wsman(object):
    def __init__(self, host):
        self.host = host
        opts = { "-h": self.get_host, "-u": self.get_user, "-p": self.get_password }
        self.wsman_cmd = copy.copy(basic_wsman_cmd)
        for k,v in opts.items():
            if v() is not None:
                self.wsman_cmd.extend([k,v()])

    def get_host(self):
        return self.host.get("host", None)

    def get_user(self):
        return self.host.get("user", None)

    def get_password(self):
        return self.host.get("password", None)

    def get_xml_from_uri(self, wsman_uri_list):
        for cmd in wsman_uri_list:
            yield call_output( self.wsman_cmd + [cmd], raise_exc=False )

class MockWsman(Wsman):
    def makesafe(self, pth):
        p = re.compile( '[^a-zA-Z0-9]')
        return p.sub( '_', pth)

    def get_xml_from_uri(self, wsman_uri_list):
        for uri in wsman_uri_list:
            xml_file = open(os.path.join(test_data_dir, self.makesafe(self.get_host()), self.makesafe(uri)), "r")
            xml_str = xml_file.read()
            xml_file.close()
            yield xml_str

@traceLog()
def stuff_xml_into_ini(host, ini, setting):
    # run each wsman command in turn, and add the info to the INI object
    wsman_uri_list = dell_uri_list[setting]
    wsman = wsman_factory(host)
    for wsman_xml in wsman.get_xml_from_uri(wsman_uri_list):
        add_options_to_ini(ini, wsman_xml)


# Create the ini file for BIOS or NIC by parsing the XML file from wsman
def add_options_to_ini(ini, wsman_xml):
    iniDict = {}
    DOMTree = xml.dom.minidom.parseString(wsman_xml)
    item_list = DOMTree.documentElement.getElementsByTagNameNS('*', 'Items')[0]
    element_node_type = xml.dom.minidom.Node.ELEMENT_NODE

    # iterate over all <Items> sub elements, we dont know what their names are
    for elem in [ e for e in item_list.childNodes if e.nodeType == element_node_type]:
        name  = getNodeText(elem.getElementsByTagNameNS('*', 'AttributeName')[0])
        fqdd  = getNodeText(elem.getElementsByTagNameNS('*', 'FQDD')[0])
        value = getNodeText(elem.getElementsByTagNameNS('*', 'CurrentValue')[0])
        moduleVerboseLog.info("Processing element: %s" % name)

        # something peculiar to idrac, no idea what at this point
        # just emulating old behaviour for now
        grpid = elem.getElementsByTagNameNS('*', 'GroupID')
        if grpid:
            name = getNodeText(grpid[0]) + "#" + name

        if not ini.has_section(fqdd):
            ini.add_section(fqdd)
        ini.set(fqdd, name, value)

# Take the XML which has the ordering of Attributes and extract the order
@traceLog()
def get_display_order(order_xml):
  DOMTree = xml.dom.minidom.parseString(order_xml)
  root_elem = DOMTree.documentElement
  attrlist = root_elem.getElementsByTagName('AttributeName')
  vallist  = root_elem.getElementsByTagName('DisplayOrder')
  orderDict = {}

  i = 0
  for attr in attrlist:
    if vallist[i].hasChildNodes() == True:
       orderDict[attr.childNodes[0].data] = int(vallist[i].childNodes[0].data)
    i = i + 1

  return orderDict



# HELPER FUNCTIONS FOR PARSING XML BELOW
def getText(nodelist):
    rc = ""
    if nodelist is not None:
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
    return rc

def getNodeText( node, *args ):
    rc = ""
    node = getNodeElement(node, *args)
    if node is not None:
        rc = getText( node.childNodes )
    return rc

def getNodeElement( node, *args ):
    if len(args) == 0:
        return node

    if node is not None:
        for search in node.childNodes:
            if isinstance(args[0], types.StringTypes):
                if search.nodeName == args[0]:
                    candidate = getNodeElement( search, *args[1:] )
                    if candidate is not None:
                        return candidate
            else:
                if search.nodeName == args[0][0]:
                    attrHash = args[0][1]
                    found = 1
                    for (key, value) in attrHash.items():
                        if search.getAttribute( key ) != value:
                            found = 0
                    if found:
                        candidate = getNodeElement( search, *args[1:] )
                        if candidate is not None:
                            return candidate
