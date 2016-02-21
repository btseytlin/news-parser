import sys
import getopt 
import os
import json
import re
from difflib import SequenceMatcher
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import Levenshtein
_debug = False
stderr_set = False

seek_partial_matches = False
partial_match_threshold = 0.65

terminator =  "[[[___]]]"
terminator_for_parsing = "[[[___]]]"

def pdebug(*args):
    """Write debug info to debug.txt if debug mode is on.

    Args:
        *args: sequence of strings to output.
    """
    if _debug:
        global stderr_set
        if not stderr_set:
            sys.stderr = open(os.path.dirname(os.path.abspath(__file__))+'\\debug.txt', 'w',encoding="utf-8")
            stderr_set = True

        print(" ".join(args),file=sys.stderr)

def combinations(n, m):
    """ C(n, m)

    Returns:
           m!
        --------
        n!(m-n)!

    """
    import math
    return math.factorial(m)/(math.factorial(n) * (math.factorial(m-n)) )

def fuzzy_levenshtein(w1, w2):
    """Check if two strings are mostly(fuzzy) similar ('Эльвира Набиуллина' and 'Набиуллина').

    Args:
        w1, w2: strings to compare.
    Returns:
        Boolean result of comparison.
    """
    ratio = Levenshtein.ratio(' '.join(sorted(w1.split())), ' '.join(sorted(w2.split())))
    global partial_match_threshold
    if ratio >= partial_match_threshold:
        return True
    return False

def compile_huge_strs(texts, huge_str_size=250):
    """Create a list of concated strings with a total of huge_str_size in each chunk to pass to tomita for processing
    Args:
        texts: list of texts to compile into huge strings.
    Returns:
        A list of huge strings made of texts separated by a special terminator.
    """
    huge_strs=[]
    cur_pos = 0
    num = huge_str_size
    #for num in range(huge_str_size, len(texts), huge_str_size):
    while cur_pos <= len(texts):
        huge_strs.append(terminator.join([text for text in texts[cur_pos:num]]))
        cur_pos = num
        num = cur_pos + huge_str_size

    #for text in texts:
        #huge_str += text + terminator
    return huge_strs


def post_process_tomita_facts(facts):
    """Remove duplicates and lowercase all facts

    Args:
        facts: dictionary of of format {'fact_type': [fact1, fact2 ... factn] }
    """
    for key in facts.keys():
        facts[key] = list(set([ x.lower() for x in facts[key] ]))
    return facts

def parse_tomita_output(text):
    """Parse tomita text output to extract fact types and facts.

    Args:
        text: String to parse.

    Returns:
        Dictionary of format {'fact_type': [fact1, fact2 ... factn] }
    """
    facts = {}
    clearing_text = str(text)
    while clearing_text.find("{") != -1:
        opening_brace = clearing_text.find("{")
        if not opening_brace:
            break
        closing_brace = clearing_text.find("}", opening_brace)
        if not closing_brace:
            break
        fact_type=re.search('(\w+\s+)(?=\s+\{)', clearing_text[:closing_brace])
        if not fact_type:
            continue
        fact_type = fact_type.group(0).strip()
        fact_body = clearing_text[opening_brace-1:closing_brace+1]
        fact_text = fact_body[fact_body.find('=')+1:-1].strip()
        if not fact_type in facts.keys():
            facts[fact_type] = []
        facts[fact_type].append(fact_text)
        clearing_text = clearing_text.replace(fact_body, '')
    return post_process_tomita_facts(facts)


def get_overlaps(facts1, facts2):
    """Find how many exactly or fuzzy same facts of each type exist in fact1 and fact2.

    Args:
        facts1, facts2: dictionaries of facts of format {'fact_type':[fact1, fact2 ... factn]}
    Returns:
        Dictionary of format {fact_type:overlap_number}
    """
    overlaps = {}
    pdebug("Seeking overlaps between\n %s\n and\n %s:"%(str(facts1), str(facts2)))
    for key in facts1.keys():
        if key in facts2.keys():
            overlaps[key] = len(frozenset(facts1[key]).intersection(facts2[key]))
            #pdebug('Complete overlaps for key %s:\n %s'%(key, str(frozenset(facts1[key]).intersection(facts2[key]))))
            if key == "EntityName" and seek_partial_matches:
                for fact in facts1[key]:
                    for fact1 in facts2[key]:
                        if fact != fact1:
                            #pdebug("fuzzy matching", fact, fact1)
                            if fuzzy_levenshtein(fact, fact1):
                                #pdebug('Partial overlap \"%s\" and \"%s\"'%(fact, fact1))
                                overlaps[key] += 1

    pdebug("Overlaps:\n %s"%(str(overlaps)))
    return overlaps

class Comparison():
    """A structure to hold results of seeking overlaps between two NewsMessage objects facts and ease outputting."""
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
    """A structure to hold information extracted from input and grammemes after parsing."""
    def __init__(self, id, title, text, cluster, date, source):
        self.id = id
        self.title = title
        self.text = text
        self.date = date
        self.source = source
        self.grammemes = []
        self.cluster = cluster

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s;%s;%s;%s;%s"%(self.id, self.title, self.text, self.cluster, "["+",".join(self.grammemes)+"]")

def preprocess(text):
    """Strip useless whitespaces and trailing \" from text.

    Args:
        text: String to preprocess.
    Returns:
        Processed text.
    """

    text = text.strip("\n \"\t").lstrip(".")

    return text

def read_input(fname):
    """Read the input file line by line.

    Args:
        fname: filename to read
    Returns:
        List of NewsMessage objects.

    """
    news_objects = []
    with open(fname, "r", encoding="utf-8-sig") as f:
        for line in f:
            #pdebug("Parsing line\n", line,"\n[[[[[==============]]]]]\n")
            atrib = [x.strip("\"").strip() for x in line.split(';')]
            news_line = NewsMessage(atrib[0], atrib[1], atrib[2], atrib[3],atrib[4], atrib[5])
            news_line.text = preprocess(news_line.text)
            #news_line.grammemes = get_grammemes(news_line.text)
            news_objects.append(news_line)
            #pdebug("[[[[[==============]]]]]")
    return news_objects

def decompile_huge_strs(tomita_output_chunks):
    #Now that we have a list of processed huge chunks we have to:
    #1. Break each chunk into separate texts (e.g. ["a[[[___]]]b[[[___]]]c"] to [ ["a", "b", "c"] ])
    lists_of_texts = [stdout_data.split(terminator_for_parsing) for stdout_data in tomita_output_chunks]
    #2. Unpack all lists of texts into one list (e.g. [ ["a", "b", "c"] ] to ["a", "b", "c"])
    huge_list = [ ] #Each i-th text in 'huge_list' is a processed i-th text in 'texts' (and a processed text of i-th news message)
    for l in lists_of_texts:
        for text in l:
                huge_list.append(text)
    return huge_list

def tomita_parse(text):
    try:
        p = Popen(['tomita/tomitaparser.exe', "tomita/config.proto"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=bytes(text, 'UTF-8'), timeout=300)
        stderr_data = stderr_data.decode("utf-8").strip()
        stdout_data = stdout_data.decode("utf-8").strip()
        print("Tomita returned:", stderr_data.replace("\n", ''))
        pdebug("Tomita returned stderr:\n", stderr_data+"\n" )
    except TimeoutExpired:
        p.kill()
        pdebug("Tomita killed due to timeout")
        print("Tomita killed due to timeout")

    return stdout_data, stderr_data

def extract_facts(news):
    """ Compile all texts into chunks of 50..250, send them to tomita for parsing, 
        put facts into NewsMessage objects. 

    Args:
        news: list on NewsMessage objects.
    Returns:
        List of NewsMessage objects.
    """
    texts = [news_line.text for news_line in news]
    text_per_chunk = min(max(int(len(texts)/20), 30), 250)
    print("Compiling texts into chunks with %d texts in each"%(text_per_chunk))
    huge_strs = compile_huge_strs(texts, text_per_chunk)
    #Pass huge str to tomita
    facts = []
    tomita_output_chunks = []
    pdebug("Sending huge str to tomita")
    total_huge_strs = len(huge_strs)
    for i in range(total_huge_strs):
        huge_str = huge_strs[i]
        print("Processing chunk %d/%d"%(i, total_huge_strs) )
        stdout_data, stderr_data = tomita_parse(huge_str)

        if i==0:
            pdebug("First huge chunk:\n/////HUGE CHUNK/////\n %s \n/////HUGE CHUNK/////\n"%(huge_str))
            pdebug("First huge chunk parsed:\n/////HUGE CHUNK PARSED/////\n %s \n/////HUGE CHUNK PARSED/////\n"%(stdout_data))

        tomita_output_chunks.append(stdout_data)

    
    huge_list = decompile_huge_strs(tomita_output_chunks)

    #pdebug("Hugelist sample, first text:\n", '\n'.join(huge_list[1]))
    pdebug("Total chunks %d, decompiled texts %d"%(total_huge_strs, len(huge_list)) )
    percentage = int(len(huge_list)*0.1)
    for i in range(len(huge_list)):
        if i % percentage == 0:
            print("Parsing tomita output %d/%d"%(i, len(huge_list)) )
        text = huge_list[i]
        facts.append(parse_tomita_output(text))

    try:
        for i in range(len(texts)):
            pdebug("For text:\n%s\nReceived facts are:\n%s"%(texts[i], str(facts[i])))
            news[i].grammemes = facts[i]
    except:
        print('news:%d, texts originally:%d, texts after parsing: %d, facts:%d, i%d'%( len(news), len(texts), len(huge_list), len(facts), i ) )
    #launch tomita
    #read tomita output from stdout
    return news 


def compare_and_output(news, fname):
    """Compare all news objects, get their overlapping facts. Write results to output file.

    Args:
        news: List of NewsMessage objects.
        fname: Output filename.
    """
    pdebug("Amount of news",str(len(news)))
    pdebug("Amount of comparisons",str(combinations(2, len(news))))
    print("Amount of news",str(len(news)), ", amount of comparisons",str(combinations(2, len(news))))
    percentage = int(len(news)*0.025)
    total_news = len(news)
    comparisons = 0
    with open(fname, 'w', encoding='utf-8') as f:
        f.write("N;ComparedIDs;Name;A;ADV;ADVPRO;ANUM;APRO;COM;CONJ;INTJ;NUM;PART;PR;SPRO;V;S;Duplicate;\n")#Table header
        for i in range(total_news):
            if i % percentage == 0:
                print("%d/%d"%(i, total_news))
            for j in range(i+1, total_news):
                pdebug("Comparing news %d and %d"%(i, j))
                comparison = Comparison(news[i], news[j])
                comparison.overlaps = get_overlaps(news[i].grammemes, news[j].grammemes)
                f.write(''.join(["%d;"%(comparisons), str(comparison)]))
                comparisons+=1

def main(argv):
    input_fname = "input.csv"
    output_fname = "output.csv"
    try:                                
        opts, args = getopt.getopt(argv, "di:o:e:p:", ["input=", "output=", "enable-partial-matching=","partial-match-threshold="])
    except getopt.GetoptError:
        print('news_parser.py [-i <input_file>] [-o <output_file>] [-e <bool>] [-p <float>]')
        sys.exit(2)   

    for opt, arg in opts:                                           
        if opt in ("-i", "--input"):
            input_fname = arg   
        elif opt in ("-o", "--output"):
            output_fname = arg
        elif opt in ("-e", "--enable-partial-matching"):
            global seek_partial_matches
            seek_partial_matches = arg.lower() == "true" or arg == '1'

        elif opt in ("-p", "--partial-match-threshold"):
            global partial_match_threshold
            partial_match_threshold = max(0.5, min(float(arg), 1))
        elif opt == '-d':
            global _debug
            _debug = True
    
    pdebug("Input file, output file:", input_fname, output_fname)
    print("Reading input file...")
    news = read_input(input_fname)
    print("Done.")
    print("Extracting facts from text...")
    news = extract_facts(news)
    print("Done.")
    print("Seeking overlaps in extracted facts and writing to output file...")
    if seek_partial_matches:
        print("Partial matching enabled. It can be slow.")
    compare_and_output(news, output_fname)
    print("Done.")
            
if __name__ == "__main__":
    main(sys.argv[1:])

