from entity import Biotope, SearchEntity, SynonymType

class ExactMatch(object):
    
    def __init__(self, ontobiotope:Biotope):
        self.ontobiotope = ontobiotope


    def match_all(self, doc_list, weighted=False):
        return [self.match_terms(doc, weighted) for doc in doc_list]


    def match_terms(self, term_list, weighted=False):
        return [self.match_term(term, weighted) for term in term_list]


    def match_term(self, term:SearchEntity, weighted=False):
        
        if weighted : return self.weighted_match_term(term)
        matched_id = '-1'

        for id in self.ontobiotope:
            biotope = self.ontobiotope[id]
            
            if term.name == biotope.name : return id # match exact habitat
            if term.name.lower() == biotope.name : return id # try lowercased-term
            if term.name[0:-1] == biotope.name : return id # in case plural from of term
            synonyms = [synonym.name for synonym in biotope.synonyms]
            for s in synonyms:
                if term.name == s : return id # try synonym
                if term.name.lower() == s : return id
            
            is_as = biotope.is_as 
            for is_a in is_as:
                if term.name == self.ontobiotope[is_a].name : matched_id = id 
        
        return matched_id


    def weighted_match_term(self, term:SearchEntity):
        
        match_scores = {}

        for id in self.ontobiotope:
            match_scores[id] = 0
            biotope = self.ontobiotope[id]
            synonyms = [(synonym.type, synonym.name_list) for synonym in biotope.synonyms]
            is_as_name_list = [self.ontobiotope[is_a].name_list for is_a in biotope.is_as]

            for name in term.name_list:
                if (name in biotope.name_list or name[0].lower()+name[1:] in biotope.name_list or name[0:-1] in biotope.name_list):match_scores[id] += (1/len(biotope.name_list))
                
                synonym_score = 0
                for (synonym_type, synonym_name_list) in synonyms:
                    alpha = 1.0 # if synonym_type == SynonymType.exact else 0.25
                    if (name in synonym_name_list or name[0].lower()+name[1:] in synonym_name_list or name[0:-1] in synonym_name_list): 
                        synonym_score += alpha/(len(synonym_name_list))
                match_scores[id] += min(synonym_score, 1)

                is_a_score = 0
                beta = 1.0
                for is_a in is_as_name_list:
                    if (name in is_a or name[0].lower()+name[1:] in is_a or name[0:-1] in is_a) : is_a_score += beta/len(is_a)
                match_scores[id] += min(is_a_score, 1)

        match_id = id
        match_score = 0
        for id in match_scores:
            if match_scores[id] > match_score:
                match_id = id
                match_score = match_scores[id]
        return match_id



        