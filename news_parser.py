import sys
import getopt 
import os
import json
import re
from difflib import SequenceMatcher
#import urllib2
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

_debug = False
stderr_set = False
def pdebug(*args):
    if _debug:

        global stderr_set
        if not stderr_set:
            sys.stderr = open(os.path.dirname(os.path.abspath(__file__))+'\\debug.txt', 'w',encoding="utf-8")
            stderr_set = True

        print(" ".join(args),file=sys.stderr)

def fuzzy_match(word1, word2):
    if len(word1) < len(word2):
        minlen_word = word1
        maxlen_word = word2
    else:
        maxlen_word = word1
        minlen_word = word2

    word1 = word1.split()
    word1.sort()
    word2 = word2.split()
    word2.sort()

    word1 = set(word1)
    word2 = set(word2)

    intersection = word1.intersection(word2)
    difference1 = list(word1 - intersection)
    difference2 = list(word2 - intersection)
    intersection = list(intersection)
    difference1.sort()
    difference2.sort()
    intersection.sort()

    t0 = " ".join(intersection)
    t1 = " ".join(intersection) + " ".join(difference1)
    t2 = " ".join(intersection) +  " ".join(difference2)

    scores = [ 
        SequenceMatcher(None, t0, t1).ratio(),
        SequenceMatcher(None, t0, t2).ratio(),
        SequenceMatcher(None, t1, t2).ratio(),
    ]

    if max(scores) > 0.65:
        return True
    return False

def post_process_tomita_facts(facts):
    for key in facts.keys():
        facts[key] = list(set([ x.lower() for x in facts[key] ]))
    return facts

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
    return post_process_tomita_facts(facts)


def get_overlaps(facts1, facts2):
    overlaps = {}
    pdebug("Seeking overlaps between\n %s\n and\n %s:"%(str(facts1), str(facts2)))
    for key in facts1.keys():
        if key in facts2.keys():
            overlaps[key] = len(frozenset(facts1[key]).intersection(facts2[key]))

            pdebug('%d complete overlaps between facts for key \"%s\"'%( overlaps[key], key))
            pdebug('Complete overlaps:\n %s'%(str(frozenset(facts1[key]).intersection(facts2[key]))))
            if key == "EntityName":
                for fact in facts1[key]:
                    for fact1 in facts2[key]:
                        if fact != fact1:
                            pdebug("fuzzy matching", fact, fact1)
                            if fuzzy_match(fact, fact1):
                                pdebug('Partial overlap \"%s\" and \"%s\"'%(fact, fact1))
                                overlaps[key] += 1

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
        line = line+"%d"%(self.message1.cluster == self.message2.cluster and not self.message1.cluster == "-" and not self.message2.cluster == "-")+";\n"
        return line


class NewsMessage():
    def __init__(self, id, title, text, cluster, date, source):
        self.id = id
        self.title = title
        self.text = text
        self.date = date
        self.source = source
        self.grammemes = []
        self.cluster = cluster

    def lineout(self):
        pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s;%s;%s;%s;%s"%(self.id, self.title, self.text, self.cluster, "["+",".join(self.grammemes)+"]")

def preprocess(text):
    text = text.strip("\"\t\n").strip().split('.')
    #pdebug(str(text))
    clear_text = []
    #prev_ended_with_1_letter = None
    for t in text:
        if not t:
            continue 
        t = t.strip("\"\t\n").strip()
        #first_word = t[:t.find(' ')].strip()
        #pdebug('rsplit',str(t.rsplit(None, 1)))
        #last_word = t.rsplit(None, 1)[-1].strip()
        #pdebug('f',first_word,'l', last_word)
        #if prev_ended_with_1_letter:
            #pdebug('ended with 1 letter')
        #if first_word.upper() != first_word and not prev_ended_with_1_letter:
        #    t = t.replace(first_word, first_word.lower(), 1)
        #prev_ended_with_1_letter = len(last_word) == 1
        clear_text.append(t)

    text = '. '.join(clear_text)
    return process_spelling(text)

def process_spelling(text):
    return text

def get_grammemes(text):
    #write text to stdin
    pdebug("Sending to tomita:\n----\n", text,"\n----")
    try:
        p = Popen(['tomita/tomitaparser.exe', "tomita/config.proto"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=bytes(text, 'UTF-8'), timeout=45)
        pdebug("Tomita returned stderr:\n", "stderr: "+stderr_data.decode("utf-8").strip()+"\n" )
    except TimeoutExpired:
        p.kill()
        pdebug("Tomita killed")
    stdout_data = stdout_data.decode("utf-8")
    facts = parse_tomita_output(stdout_data)
    pdebug('Received facts:\n----\n',str(facts),"\n----")
    #launch tomita
    #read tomita output from stdout
    return facts 

def read_input(fname):
    news_objects = []
    with open(fname, "r", encoding="utf-8-sig") as f:
        for line in f:
            pdebug("Parsing line\n", line,"\n[[[[[==============]]]]]\n")
            atrib = [x.strip("\"").strip() for x in line.split(';')]
            news_line = NewsMessage(atrib[0], atrib[1], atrib[2], atrib[3],atrib[4], atrib[5])
            news_line.text = preprocess(news_line.text)
            news_line.grammemes = get_grammemes(news_line.text)
            news_objects.append(news_line)
            pdebug("[[[[[==============]]]]]")
    return news_objects

def compare(news):
    comparisons = []
    pdebug("Amount of news",str(len(news)))
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

