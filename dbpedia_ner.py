#!/usr/bin/env python

from KafNafParserPy import *
from urllib2 import Request, urlopen
from urllib import urlencode
from lxml import etree
import sys
import os
import argparse

############# CHANGES #################################
# 0.1 (9-jan-2015) --> first working version
# 0.2 (12-jan-2015) --> included KAF/NAF headers
#######################################################

DBPEDIA_REST = 'http://spotlight.sztaki.hu:2222/rest/candidates'
os.environ['LC_ALL'] = 'en_US.UTF-8'
__this_name__ = 'dbpedia_spotlight_cltl'
__this_version__ = '0.2'

def call_dbpedia_rest_service(this_text,url,confidence):
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
    
    my_lp = Clp()
    my_lp.set_name(__this_name__)   
    my_lp.set_version(__this_version__)
    my_lp.set_timestamp()
    
    naf_obj.add_linguistic_processor('entities',my_lp)
    
    
    
              
if __name__ == '__main__':
    parser_opts = argparse.ArgumentParser(description='Calls to DBPEDIA spotlight online to extract entities and the links to DBPEDIA',
                                          usage='cat myfile.naf | '+sys.argv[0]+' [OPTIONS]')
    parser_opts.add_argument('-url', dest='dbpedia_url',default=DBPEDIA_REST, help='URL of the DBPEDIA rest webservice, by default:'+DBPEDIA_REST)
    parser_opts.add_argument('-c', dest='confidence', type=float,default=0.5, help='Minimum confidence of candidates for the DBPEDIA links')
    
    args = parser_opts.parse_args()
    
    if sys.stdin.isatty():
        parser_opts.print_help()
        sys.exit(-1)
        
    #################################
    # 1.- Get the raw text from the input file#
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
    # 2.- Call to the REST service
    #################################
    dbpedia_xml_results = call_dbpedia_rest_service(whole_text,args.dbpedia_url,args.confidence)

    #################################
    # 3.- Add the entities and dbpedia links to the object (passed by reference)
    #################################
    load_entities_into_object(parser, dbpedia_xml_results)
    
    
    #################################
    # 4.- Dump the result
    #################################
    parser.dump()

    
