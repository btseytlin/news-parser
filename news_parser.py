import sys
import getopt 
import os
import json
import re
from difflib import SequenceMatcher
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

_debug = False
stderr_set = False

seek_partial_matches = False
partial_match_threshold = 0.65

terminator =  ".[[[___]]]"
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

def fuzzy_match(word1, word2):
    """Check if two strings are mostly(fuzzy) similar ('Эльвира Набиуллина' and 'Набиуллина').
    
    Three pairs are created for comparison
    t0 = [SORTED_STRING_INTERSECTION] (For the above example its 'Набиуллина')
    t1 = [SORTED_STRING_INTERSECTION] + [SORTED_Difference1] (For the above example its 'Эльвира')
    t2 = [SORTED_STRING_INTERSECTION] + [SORTED_Difference2] (For the above example its '')
    All components are sorted alphabetically so that word order doesn't matter.
    This algorithm makes it so the score is bigger the more common words strings have AND the more similar the other words are.

    Args:
        word1, word2: strings to compare.
    Returns:
        Boolean result of comparison.
    """
    if SequenceMatcher(None, word1, word2).quick_ratio() < 0.5: #Get a quick calculation and reject absolutely different strings before we get to real lengthy calculations
        return False

    word1 = set(word1.split())
    word2 = set(word2.split())

    intersection = word1.intersection(word2)
    difference1 = list(word1 - intersection)
    difference2 = list(word2 - intersection)
    intersection = list(intersection)
    difference1.sort()
    difference2.sort()
    intersection.sort()

    t0 = " ".join(intersection)
    t1 = " ".join(intersection) +' '+ " ".join(difference1)
    t2 = " ".join(intersection) +' '+  " ".join(difference2)

    seq_matcher = SequenceMatcher(None, t0, t1)
    score1 = seq_matcher.ratio()
    seq_matcher.set_seqs(t0, t2)
    score2 = seq_matcher.ratio()
    seq_matcher.set_seqs(t1, t2)
    score3 = seq_matcher.ratio()

    global partial_match_threshold
    if max(score1, score2, score3) > partial_match_threshold:
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
        huge_strs.append(''.join([text +terminator for text in texts[cur_pos:num] if text]))
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
                            if fuzzy_match(fact, fact1):
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
    text = text.strip("\"\t\n").strip().split('.')
    clear_text = []
    for t in text:
        if not t:
            continue 
        t = t.strip("\"\t\n").replace('\n', '').strip()
        clear_text.append(t)

    text = '. '.join(clear_text)
    return text

# CURRENTLY NOT IN USE
def get_grammemes(text):
    """Send a single news message text to tomita parser, parse output to extract facts.

    Args:
        text: String to pass to tomita for parsing
    Returns:
        List of facts dictionaries.

    """

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

def extract_facts(news):
    """ Compile all texts into chunks of 50..250, send them to tomita for parsing, 
        put facts into NewsMessage objects. 

    Args:
        news: list on NewsMessage objects.
    Returns:
        List of NewsMessage objects.
    """
    texts = [news_line.text for news_line in news]
    huge_strs = compile_huge_strs(texts, 200)
    #Pass huge str to tomita
    facts = []
    #pdebug("Sending huge str to tomita")
    for huge_str in huge_strs:
        try:
            p = Popen(['tomita/tomitaparser.exe', "tomita/config.proto"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            stdout_data, stderr_data = p.communicate(input=bytes(huge_str, 'UTF-8'), timeout=360)
            stderr_data = stderr_data.decode("utf-8").strip()
            pdebug("Tomita returned stderr:\n", stderr_data+"\n" )
        except TimeoutExpired:
            p.kill()
            pdebug("Tomita killed due to timeout")
        stdout_data = stdout_data.decode("utf-8")
        huge_list = stdout_data.split(terminator_for_parsing)

        for text in huge_list:
            if text:
                facts.append(parse_tomita_output(text))

    try:

        for i in range(len(texts)):
            pdebug("For text:\n%s\nReceived facts are:\n%s"%(texts[i], str(facts[i])))
            news[i].grammemes = facts[i]
    except:
        print(i)
        print(len(texts))
        print(len(facts))
    #launch tomita
    #read tomita output from stdout
    return news 


def compare(news):
    """Compare all news objects, get their overlapping facts.

    Args:
        news: List of NewsMessage objects.
    Returns:
        List of Comparison objects.
    """

    comparisons = []
    pdebug("Amount of news",str(len(news)))
    percentage = int(len(news)*0.025)
    for i in range(len(news)):
        if i % percentage == 0:
            print("%d/%d"%(i, len(news)))
        for j in range(i+1, len(news)):
            pdebug("Comparing news %d and %d"%(i, j))
            comparison = Comparison(news[i], news[j])
            comparison.overlaps = get_overlaps(news[i].grammemes, news[j].grammemes)
            comparisons.append(comparison)
    return comparisons

def output(comparisons, fname):
    """Write results to output file.

    Args:
        comparisons: List of Comparison objects.
        fname: Output filename.
    """
    with open(fname, 'w', encoding='utf-8') as f:
        f.write("N;ComparedIDs;Name;A;ADV;ADVPRO;ANUM;APRO;COM;CONJ;INTJ;NUM;PART;PR;SPRO;V;S;Duplicate;\n")#Table header
        for i in range(len(comparisons)):
            comparison = comparisons[i]
            f.write("%d;"%(i) + str(comparison))

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
        elif opt in ("-p", "--partial-match-threshold"):
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
    print("Seeking overlaps in extracted facts...")
    comparisons = compare(news)
    print("Done.")
    print("Writing results to output file...")
    output(comparisons, output_fname)
    print("Done.")
            
if __name__ == "__main__":
    main(sys.argv[1:])

