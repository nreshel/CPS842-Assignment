import re
import sys
import json
import pprint
import stemmer
from stemmer import PorterStemmer
class Invert:
    def __init__(self):
        self.query = '' 
        self.parsed_doc = {} 
        self.parsed_postlist = {} 
        self.parsed_dicionary = {}
        self.stem_answer = '' 

    ps = PorterStemmer()

    def index_query(self, q, p_doc, s_answer):
        with open('posting_list.json') as posting_file:
            p_postlist = json.load(posting_file)
        with open('dictionary.json') as dict_file:
            p_dict = json.load(dict_file)
        self.query = q
        self.parsed_doc = p_doc
        self.parsed_postlist = p_postlist
        self.parsed_dicionary = p_dict
        self.stem_answer = s_answer
        index_dict = {}
        first_item = []
        abstract = ''
        summary = ''
        abstract_list = []
        ps = PorterStemmer()
        if self.stem_answer == 'no':
            stem_query = self.query
        if self.stem_answer == 'yes':    
            stem_query = ps.stem(self.query, 0, len(self.query)-1)
        for term, value in self.parsed_postlist.items():
            if stem_query == term:
                if isinstance(value, dict):
                    for doc_id, val in value.items():
                        if term not in index_dict:
                            index_dict[term] = {}
                            index_dict[term]['documents'] = []
                            index_dict[term]['summary'] = ''

                        if self.query in self.parsed_doc[doc_id]['abstract'] and len(first_item) == 0:
                            first_item.append(self.parsed_doc[doc_id]['abstract'])
                            abstract = first_item[0]
                            abstract_list = abstract.split()
                            summary = abstract_list[abstract_list.index(self.query)]
                            count = 0
                            while count < 10:
                                if abstract_list.index(self.query) + count < len(abstract_list):
                                    index_dict[term]['summary'] += abstract_list[abstract_list.index(self.query) + count] + ' '
                                else:
                                    break
                                count += 1

                        if doc_id not in index_dict[term]:
                            index_dict[term][doc_id] = {}
                            index_dict[term][doc_id]['position'] = val['position']
                            index_dict[term][doc_id]['term_frequency'] = val['frequency']
                            index_dict[term][doc_id]['title'] = self.parsed_doc[doc_id]['title']
                        index_dict[term]['doc_frequency'] = self.parsed_dicionary[term]
                        index_dict[term]['documents'].append(doc_id)
        pprint.pprint(index_dict)