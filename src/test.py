import re
import sys
import time
import json
import pprint
import stemmer
import invert

from stemmer import PorterStemmer
from invert import Invert

invert = Invert()
keep_loop = ''
while keep_loop != 'ZZEND'.lower():
    start_time = time.clock()
    stop_question = raw_input("would you like stop words? (yes/no)")
    stem_question = raw_input("would you like stemming? (yes/no)")

    def parse_cacm(dictionary):
        f = open("cacm/cacm.all", "r")
        regexI = r"^[.]+[I]\s"
        regexT = r"^[.]+[T]\s"
        regexW = r"^[.]+[W]\s"
        regexB = r"^[.]+[B]\s"
        regexA = r"^[.]+[A]\s"
        regexN = r"[.]+[N]\s"
        regex = r"[.]+[A-Z]\s"
        for line in f:
            if re.match(regexI, line):
                x = line.split()
                doc = x[0]
                doc_id = x[1]
                dictionary[doc_id] = {}
                dictionary[doc_id]['id']=doc_id
            
            if re.match(regexT, line):
                dictionary[doc_id]['title']= f.next().replace('\n', '')

            if re.match(regexW, line):
                description = ''
                next_line = f.next()
                while not(re.match(regex, next_line)):
                    description += next_line.replace('\n', '')
                    next_line = f.next()
                dictionary[doc_id]['abstract'] = description

            if re.match(regexB, line):
                dictionary[doc_id]['published']= f.next()
                
            if re.match(regexA, line):
                dictionary[doc_id]['author']= f.next()

            if re.match(regexN, line):
                dictionary[doc_id]['released']= f.next()
        
        print("Finished parsing CACM.all")
        return dictionary

    def get_postlist(stop_answer, stem_answer, dict_terms):
        if stop_answer == 'no':
            stopwords = []
        if stop_answer == 'yes':
            stopwords = ['i','a','about','an','and','are','as','at','be','by','for','from','how','in','is','it','of','on','or','that','the','this','to','was','what','when','where','who','will','with','the']
        ps = PorterStemmer()
        position_list = []
        dict_posting = {}
        counter = 0
        for key, value in dict_terms.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == 'abstract':
                        val = v.replace(',', '').lower().split()
                        for index, word in enumerate(val):
                            if stem_answer == 'no':
                                stem_word = word
                            if stem_answer == 'yes':
                                stem_word = ps.stem(word, 0,len(word)-1)
                            if stem_word not in stopwords:
                                if stem_word not in dict_posting:
                                    dict_posting[stem_word] = {}
                                if key not in dict_posting[stem_word]:
                                    dict_posting[stem_word][key] = {}
                                    dict_posting[stem_word][key]['frequency'] = 0
                                    dict_posting[stem_word][key]['position'] = []

                                dict_posting[stem_word][key]['frequency'] += 1
                                dict_posting[stem_word][key]['position'].append(index)
            with open('posting_list.json', 'w') as outfile:
                json.dump(dict_posting, outfile)
            print("Finished writing the posting list")
        return dict_posting

    def get_dictionary(dict_terms):
        dict_freq = {}
        for term, doc_id in dict_terms.items():
            if term not in dict_freq:
                dict_freq[term] = len(doc_id)
        with open('dictionary.json', 'w') as outfile:
            json.dump(dict_freq, outfile)
        print("Finished writing the dicitionary")
        return dict_freq

    parse_dictionary = {}
    parsed_doc = parse_cacm(parse_dictionary)
    parsed_postlist = get_postlist(stop_question, stem_question, parsed_doc)
    parsed_dictionary = get_dictionary(parsed_postlist)

    query = raw_input("Type out a word you would like to search: ")

    invert.index_query(query, parsed_doc, stem_question)

    print("Inverted index program executed in: ")
    print time.clock() - start_time, "seconds"

    keep_loop = raw_input("Would you like to keep searching? Enter any word or letter to contiune, type in ZZEND to stop ").lower()