# dbpedia_ner
Named Entity Recogniser (NER) and entity linker to dbpedia entries based on Dbpedia spotlight for KAF/NAF files.

##How to install it##
You will need just to clone this repository first, and get the [KafNafParserPy](https://github.com/cltl/KafNafParserPy) module for reading and writing KAF/NAF files. So in summary:

1. Go to the folder where you want to install this repository
2. Clone this repository `git clone https://github.com/rubenIzquierdo/dbpedia_ner`
3. Change to the directory `cd dbpedia_ner`
4. Clone the KafNafParserPy `git clone https://github.com/cltl/KafNafParserPy`

And that's it, the system is ready to be used.


##Usage##

After the installation steps, you can test if module works by trying with the example file:
```shell
cat example.naf | python dbpedia_ner.py
```

You can see the parameters of the script by calling to it with the `-h` parameter:
```shell
python dbpedia_ner.py -h
usage: cat myfile.naf | ./dbpedia_ner.py [OPTIONS]

Calls to DBPEDIA spotlight online to extract entities and the links to DBPEDIA

optional arguments:
  -h, --help        show this help message and exit
  -url DBPEDIA_URL  URL of the DBPEDIA rest webservice, by
                    default: http://spotlight.sztaki.hu:2222/rest/candidates
  -c CONFIDENCE     Minimum confidence of candidates for the DBPEDIA links
  -re, --remove-entities
                        Remove the entities already existing in the input (if
                        any)
```

There are three optional parameters, the URL to the REST endpoint of the dbpedia webservice, and the minimum confidence allowed for the candidates for dbpedia links.
The `-re` or `--remove-entities` allows you to remove any existing entity in the input (these entities will be removed just from the output, not from the real input object)

##Contact##
* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl  rubensanvi@gmail.com
* http://rubenizquierdobevia.com/