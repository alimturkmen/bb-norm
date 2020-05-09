from entity import Biotope, SearchEntity

class ExactMatch(object):
    
    def __init__(self, ontobiotope:Biotope):
        self.ontobiotope = ontobiotope


    def match_all(self, doc_list:list):
        return [self.match_terms(doc) for doc in doc_list]


    def match_terms(self, term_list:list):
        return [self.match_term(term) for term in term_list]


    def match_term(self, term:SearchEntity):
        
        matched_id = -1

        for id in self.ontobiotope:
            biotope = self.ontobiotope[id]
            
            if term.name == biotope.name : return id # match exact habitat
            if term.name.lower() == biotope.name : return id # try lowercased-term
            if term.name[0:-1] == biotope.name : return id # in case plural from of term
            synonyms = [synonym.name for synonym in biotope.synonyms]
            for s in synonyms:
                if term.name == s : return id # try synonym
            
            is_as = biotope.is_as 
            for is_a in is_as:
                if term.name == self.ontobiotope[is_a].name : matched_id = id 
        
        return matched_id

'''        
class WeightedMatch(object):
    
    def __init__(self, ontobiotope:Biotope):
        self.ontobiotope = ontobiotope


    def match_all(self, doc_list:list):
        return [self.match_terms(doc) for doc in doc_list]


    def match_terms(self, term_list:list):
        return [self.match_term(term) for term in term_list]


    def match_term(self, term:SearchEntity):
        
        match_counts = {}
        for id in self.ontobiotope:
            biotope = self.ontobiotope[id]

            for name in term.name_list:
                if name in biotope.name_list
                    if name in match_counts : match_counts[name] += 1
                    else : match_counts[name] = 1
                if name in 
            
            for synonym in biotope.synonyms:
                name = synonym.name_list
                type = synonym.type
                if term.name in synonym.name_list

            for name in term.name_list:
                if name in biotope.name_list : 
                    if name in match_counts : match_counts[name]+=1
                    else: match_counts[name] = 1
                if name in biotope.name_list : 
                    if name in match_counts : match_counts[name]+=1
                    else: match_counts[name] = 1
'''


        