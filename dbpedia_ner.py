#!/usr/bin/env python

from KafNafParserPy import *
import sys
from urllib2 import Request, urlopen
from urllib import urlencode
from lxml import etree

DBPEDIA_REST = 'http://spotlight.sztaki.hu:2222/rest/candidates'

def call_dbpedia_rest_service(this_text,confidence=0.5):
    #curl http://spotlight.sztaki.hu:2222/rest/candidates --data-urlencode "text=$text" \ --data "confidence=0.5" --data "support=20"
    my_data = {}
    my_data['text'] = this_text.encode('utf-8')
    my_data['confidence'] = confidence
    my_data['support'] = '20'
    
    req = Request(DBPEDIA_REST, data = urlencode(my_data))
    handler = urlopen(req)
    dbpedia_xml_results = handler.read()
    handler.close()
    return dbpedia_xml_results


def load_entities_into_object(naf_obj, dbpedia_xml_results):
    term_for_token = {}
    for term in naf_obj.get_terms():
        for token_id in term.get_span().get_span_ids():
            term_for_token[token_id] = term.get_id()
    
    term_for_offset = {}
    for token in naf_obj.get_tokens():
        t = token.get_text()
        o = int(token.get_offset())
        for n in range(len(t)):
            term_for_offset[o+n] = term_for_token[token.get_id()]

    spot = etree.fromstring(dbpedia_xml_results)
    num_e = 1
    for surface_form in spot.findall('surfaceForm'):
        text = surface_form.get('name')
        begin = int(surface_form.get('offset'))
        end = begin + len(text)

        term_ids = []
        for o in range(begin,end+1):
            if o in term_for_offset:
                new_id = term_for_offset[o]
                if new_id not in term_ids:
                    term_ids.append(new_id)
        new_entity = Centity()
        new_entity.set_id('e'+str(num_e))
        num_e += 1
        new_entity.set_comment(text)
        
        ref = Creferences()
        ref.add_span(term_ids)
        new_entity.add_reference(ref)  
        
        types = []
        for resource in surface_form.findall('resource'):
            uri = resource.get('uri')
            conf = resource.get('contextualScore')
            resource_str = 'spotlight_cltl'
            reference = 'http://dbpedia.org/resource/'+uri
            ext_ref = CexternalReference()
            ext_ref.set_resource(resource_str)
            ext_ref.set_reference(reference)
            ext_ref.set_confidence(conf)
            new_entity.add_external_reference(ext_ref)
            this_type = resource.get('types','MISC')
            types.append((this_type,float(conf)))
        
        best_type = 'MISC'
        if len(types) != 0:
            best_type = sorted(types,key=lambda t: -t[1])[0][0]
        new_entity.set_type(best_type) 
        
        naf_obj.add_entity(new_entity)
    
    
    
              
if __name__ == '__main__':

    #################################
    # Get the raw text from the input file#
    #################################

    whole_text = '' #will be unicode
    parser = KafNafParser(sys.stdin)
    prev = None
    for token in parser.get_tokens():
        t = token.get_text()
        s = token.get_sent()
        if prev != None and s != prev:
            whole_text = whole_text.strip()+'\n'
        whole_text+=t+' '
        prev = s
    #################################
    
    #################################
    # Call to the REST service
    #################################
    dbpedia_xml_results = call_dbpedia_rest_service(whole_text)
    #################################
    # Add the entities and dbpedia links to the object (passed by reference)
    #################################
    load_entities_into_object(parser, dbpedia_xml_results)
    
    
    #################################
    # Dump the result
    #################################
    parser.dump()

    
