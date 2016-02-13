import sys
import getopt 
import os
import json
import re
#import urllib2
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

_debug = True
sys.stderr = open(os.path.dirname(os.path.abspath(__file__))+'\\debug.txt', 'w',encoding="utf-8")
def pdebug(*args):
    if _debug:
        print(" ".join(args),file=sys.stderr)

def parse_tomita_output(text):
    facts = {}
    clearing_text = str(text)
    while clearing_text.find("{") != -1:
        opening_brace = clearing_text.find("{")
        if not opening_brace:
            break

        
        closing_brace = clearing_text.find("}", opening_brace)
        if not closing_brace:
            break
        fact_type=re.search('(\w+\s+)(?=\s+\{)', clearing_text[:closing_brace]).group(0).strip()
        fact_body = clearing_text[opening_brace-1:closing_brace+1]
        fact_text = fact_body[fact_body.find('=')+1:-1].strip()
        if not fact_type in facts.keys():
            facts[fact_type] = []
        facts[fact_type].append(fact_text)
        clearing_text = clearing_text.replace(fact_body, '')
    return facts



class NewsMessage():
    def __init__(self, id, title, text, cluster, grammemes):
        self.id = id
        self.title = title
        self.text = text
        self.grammemes = grammemes
        self.cluster = cluster

    def lineout(self):
        pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s;%s;%s;%s;%s"%(self.id, self.title, self.text, self.cluster, "["+",".join(self.grammemes)+"]")

# not done
# def json_post_yandex_speller(text):
#     data = {
#         'text': text
#     }
#     req = urllib2.Request('http://speller.yandex.net/services/spellservice.json/checkText')
#     req.add_header('Content-Type', 'application/json')
#     response = urllib2.urlopen(req, json.dumps(data))

#     response = json.loads(response)
#     return response

def clean_up(text):
    text = text.strip("\"\t\n").strip().split('.')
    pdebug(str(text))
    clear_text = []
    for t in text:
        #pdebug("before strip", t)
        t = t.strip("\"\t\n").strip()
        clear_text.append(t)
        #pdebug("after strip", t)
        #pdebug(str(clear_text))
    text = '.'.join(clear_text)
    pdebug("processed text", text)
    return process_spelling(text)

def process_spelling(text):
    return text

def get_names(text):

    #write text to stdin
    pdebug("Sending to tomita:", text)
    try:
        p = Popen(['tomita/tomitaparser.exe', "tomita/config.proto"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=bytes(text, 'UTF-8'), timeout=45)
        pdebug("Tomita returned:", "stdout: "+stdout_data.decode("utf-8"), "stderr: "+stderr_data.decode("utf-8") )
    except TimeoutExpired:
        p.kill()
        pdebug("Tomita killed")
    stdout_data = stdout_data.decode("utf-8")
    pdebug('Received facts:',str(parse_tomita_output(stdout_data)))
    #launch tomita
    #read tomita output from stdout
    return stdout_data 

def get_grammemes(text):
    names = get_names(text)
    pdebug('Names:',str(names))
    return names

def read_input(fname):
    news_objects = []
    with open(fname, "r", encoding="utf-8") as f:
        for line in f:
            pdebug("Parsing line\n", line,"\n")
            atrib = line.split(';')
            news_line = NewsMessage(atrib[0], atrib[1], atrib[2], atrib[3], [])
            news_line.text = clean_up(news_line.text)
            news_line.grammemes = get_grammemes(news_line.text)
            news_objects.append(news_line)
    return news_objects

def compare(news):
    comparisons = []
    for i in range(len(news)):
        for j in range(i, len(news)):
            comparison = []
            comparisons.append(comparison)

    return comparisons

def output(comparisons, fname):
    return None
    with open(fname, 'w', encoding='utf-8') as f:
        for comparison in comparisons:
            pdebug(comparison.lineout())
            f.write(comparison.lineout()+"\n")

def main(argv):
    input_fname = "input.csv"
    output_fname = "output.csv"
    try:                                
        opts, args = getopt.getopt(argv, "di:o:", ["input=", "output="])
    except getopt.GetoptError:
        print('news_parser.py -i <input_file> -o <output_file>')
        sys.exit(2)   

    for opt, arg in opts:                                           
        if opt in ("-i", "--input"):
            input_fname = arg   
        elif opt in ("-o", "--output"):
            output_fname = arg
        elif opt == '-d':
            global _debug
            _debug = True
    
    pdebug("Input file, output file:", input_fname, output_fname)

    news = read_input(input_fname)
    comparisons = compare(news)
    output(comparisons, output_fname)
    
            
if __name__ == "__main__":
    main(sys.argv[1:])

