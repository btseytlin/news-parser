import sys
import getopt 
import os
import json
import urllib2
_debug = True
sys.stderr = open(os.path.dirname(os.path.abspath(__file__))+'\\debug.txt', 'w',encoding="utf-8")
def pdebug(*args):
    if _debug:
        print(" ".join(args),file=sys.stderr)

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
def json_post_yandex_speller(text):
    data = {
        'text': text
    }
    req = urllib2.Request('http://speller.yandex.net/services/spellservice.json/checkText')
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(data))

    response = json.loads(response)
    return response

def process_spelling(text):
    return text

def get_names(text):
    return text 

def get_grammemes(text):
    names = get_names(text)
    return text.split()

def read_input(fname):
    news_objects = []
    with open(fname, "r", encoding="utf-8") as f:
        for line in f:
            pdebug("Parsing line\n", line,"\n")
            atrib = line.split(';')
            news_line = NewsMessage(atrib[0], atrib[1], atrib[2], atrib[3], [])
            news_line.text = process_spelling(news_line.text)
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

