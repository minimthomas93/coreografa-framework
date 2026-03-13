from xmljson import badgerfish as bf
from defusedxml.cElementTree import fromstring as safe_fromstring, ParseError
from across_func.eval_subjects.xml.hypothetical_xml_consumer_v04.xml2json import xml_element_to_dict

# v02: BadgerFish-based conversion
def xml_v02(tree):
    try:
        xml_str = str(tree)
        root = safe_fromstring(xml_str)
        return bf.data(root)   
    except ParseError:
        return None  

# v04: Custom dict-based conversion
def xml_v04(tree):
    try:
        xml_str = str(tree)
        root = safe_fromstring(xml_str)
        return xml_element_to_dict(root) 
    except ParseError:
        return None
