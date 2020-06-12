from enum import Enum
from typing import List


class EntityType(Enum):
    phenotype = "Phenotype"
    habitat = "Habitat"


class BiotopeContext:
    def __init__(self, sentence: str, index: int):
        self.sentence = sentence
        self.index = index


class SearchEntity:
    def __init__(self, annotation_id: str, type: EntityType, name: str, str_begin: int, str_end: int):
        self.id = annotation_id
        self.name = name
        self.begin = str_begin
        self.end = str_end

        self.name_list = list(filter(lambda x: len(x) > 0, name.split(' ')))
        self.type = type


class SearchLabel:
    def __init__(self):
        self.entities = {}

    def add(self, annotation_id: str, term_id: str):
        self.entities[annotation_id] = term_id


class SynonymType(Enum):
    exact = "EXACT"
    related = "RELATED"


class Synonym:
    def __init__(self, type: SynonymType, name: str):
        self.type = type
        self.name = name
        self.name_list = list(filter(lambda x: len(x) > 0, name.split(' ')))


class Biotope:
    def __init__(self, onto_id=-1, name="", synonyms: List[Synonym] = None, is_as: List[str] = None):
        if synonyms is None:
            synonyms = []
        if is_as is None:
            is_as = []

        self.id = onto_id
        self.name = name
        self.name_list = []
        self.synonyms = synonyms
        self.is_as = is_as
