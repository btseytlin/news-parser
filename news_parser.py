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

def get_overlaps(facts1, facts2):
    overlaps = {}
    pdebug("Seeking overlaps between\n %s\n and\n %s:"%(str(facts1), str(facts2)))
    for key in facts1.keys():
        if key in facts2.keys():
            overlaps[key] = len(frozenset(facts1[key]).intersection(facts2[key]))
    pdebug("Overlaps:\n %s"%(str(overlaps)))
    return overlaps

class Comparison():
    def __init__(self, message1, message2):
        self.message1 = message1
        self.message2 = message2

        self.overlaps = {}

    def __repr__(self):
        table_fields = ["EntityName","A", "ADV", "ADVPRO", "ANUM", "APRO", "COM", "CONJ", "INTJ","NUM","PART","PR","SPRO","V", "S"]
        line = "%s:%s;"%(self.message1.id,self.message2.id)
        for field in table_fields:
            if field in self.overlaps.keys():
                line= line + str(self.overlaps[field]) + ";"
            else:
                line = line + str(0)+";"
        line = line+"%d"%(self.message1.cluster == self.message2.cluster and not self.message1.cluster == -1 and not self.message2.cluster == -1)+";\n"
        return line


class NewsMessage():
    def __init__(self, id, title, text, cluster, date, source):
        self.id = id
        self.title = title
        self.text = text
        self.date = date
        self.source = source
        self.grammemes = []
        if cluster == "-":
            cluster = -1
        else:
            cluster = int(cluster)
       

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
    clear_text = []
    for t in text:
        t = t.strip("\"\t\n").strip()
        first_word = t[:t.find(' ')]
        t = t.replace(first_word, first_word.lower())
        clear_text.append(t)

    text = '.'.join(clear_text)
    return process_spelling(text)

def process_spelling(text):
    return text

def get_grammemes(text):
    #write text to stdin
    pdebug("Sending to tomita:", text)
    try:
        p = Popen(['tomita/tomitaparser.exe', "tomita/config.proto"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=bytes(text, 'UTF-8'), timeout=45)
        pdebug("Tomita returned stderr:", "stderr: "+stderr_data.decode("utf-8").strip()+"\n" )
    except TimeoutExpired:
        p.kill()
        pdebug("Tomita killed")
    stdout_data = stdout_data.decode("utf-8")
    facts = parse_tomita_output(stdout_data)
    pdebug('Received facts:',str(facts))
    #launch tomita
    #read tomita output from stdout
    return facts 

def read_input(fname):
    news_objects = []
    with open(fname, "r", encoding="utf-8") as f:
        for line in f:
            pdebug("Parsing line\n", line,"\n")
            atrib = [x.strip("\"").strip() for x in line.split(';')]
            news_line = NewsMessage(atrib[0], atrib[1], atrib[2], atrib[3],atrib[4], atrib[5])
            news_line.text = clean_up(news_line.text)
            news_line.grammemes = get_grammemes(news_line.text)
            news_objects.append(news_line)
    return news_objects

def compare(news):
    comparisons = []
    pdebug("Amount of news, expected amount of comparisons",str(len(news)), str(len(news)*len(news)))
    for i in range(len(news)):
        for j in range(i+1, len(news)):
            pdebug("Comparing news %d and %d"%(i, j))
            comparison = Comparison(news[i], news[j])
            comparison.overlaps = get_overlaps(news[i].grammemes, news[j].grammemes)
            comparisons.append(comparison)
    return comparisons

def output(comparisons, fname):
    with open(fname, 'w', encoding='utf-8') as f:
        f.write("N;ComparedIDs;Name;A;ADV;ADVPRO;ANUM;APRO;COM;CONJ;INTJ;NUM;PART;PR;SPRO;V;S;Duplicate;\n")#Table header
        for i in range(len(comparisons)):
            comparison = comparisons[i]
            f.write("%d;"%(i) + str(comparison))

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

