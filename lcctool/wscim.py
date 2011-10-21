import pywbem.cim_obj as cobj
import schemas
from schemas import std_xml_namespaces, etree
from stdcli.trace_decorator import traceLog, getLog

# Outline:
#  The idea with this module is that we should be able to use the python pywbem 
# module to save ourselves a lot of work. Unfortunately, the schema for WSMAN
# CIM objects is completely different from WBEM CIM objects, even though they
# use the same underlying class layout.
#
# So, this module does impedance maching... it reads WSMAN XML schemas and
# creates PYWBEM objects. It also has helper methods for serializing to INI, as
# well as a class layout to let you specify the properties of a specific CIM
# class. (Eventually we should be able to read MOF files to get the class
# layout instead of manually specifying them. Manual specification is sort of a
# hack to get everything up and running quickly.)
#


##
## first up, some new methods for CIMInstance that we will monkey-patch in
##

# This is a method that will serialize "CurrentValue" to an INI file.
@traceLog()
def serialize_ini(self, ini):
    name = self["attributename"]
    if self.has_key("groupid") and self["groupid"]:
        name = self["groupid"] + "#" + name

    for sec in ("main", self["fqdd"]):
        if not ini.has_section(sec):
            ini.add_section(sec)
    ini.set(self["fqdd"], name, self["currentvalue"])

if not hasattr(cobj.CIMInstance, "serialize_ini"):
    cobj.CIMInstance.serialize_ini  = serialize_ini


class WSInstance(cobj.CIMInstance):
    def __init__(self, *args, **kargs):
        # look up all the classes in our inheritance heirarchy and add the
        # property_list parameters
        for cls in self.__class__.mro():
            self.set_class_vals(cls, args, kargs)
        cobj.CIMInstance.__init__(self, *args, **kargs)

    # set up property_list parameter based on class _property_list attribute
    def set_class_vals(self, cls, args, kargs):
        kargs["classname"] = kargs.get("classname", cls.__name__)
        for (i,typ) in getattr(cls, "_property_list", {}).items():
            # next line may look loop invariant, but we dont want to add a
            # property_list karg unless a class has a _property_list, so we can
            # only do it in the loop
            kargs["property_list"] = kargs.get("property_list", [])
            kargs["property_list"].append(i)

            # dont add 'properties' karg unless we absolutely need it
            kargs["properties"] = kargs.get("properties", {})
            # if no property present, add an empty none-type version
            if not kargs["properties"].has_key(i):
                kargs["properties"][i] = cobj.CIMProperty(i, None, type=typ)
            
@traceLog()
def cim_instance_from_wsxml(elem):
    namespace = elem.tag.split("}")[0][1:]
    cls = elem.tag.split("}")[1]
    kargs = {}
    for child in list(elem):
        attr_ns = child.tag.split("}")[0][1:]
        attr = child.tag.split("}")[1]
        if attr_ns != namespace:
            continue
        kargs[attr] = child.text

    i = find_class(namespace, cls)(classname=cls)
    i.update_existing(kargs)
    i.raw_xml_str = etree.tostring(elem)
    i.raw_xml_elem = elem
    return i

class ClassNotFound(Exception): pass

@traceLog()
def find_class(namespace, classname):
    for cls in itersubclasses(WSInstance):
        if getattr(cls, "_ns", None) == namespace:
            if cls.__name__ == classname:
                return cls

    raise ClassNotFound("Could not find match for class: %s in namespace %s" % (classname, namespace))
    #return WSInstance

## helper function to iterate subclasses
@traceLog()
def itersubclasses(cls, _seen=None):
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub

import wscim_classes
