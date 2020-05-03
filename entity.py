from enum import Enum
from typing import List


class EntityType(Enum):
    microorganism = "Microorganism"
    phenotype = "Phenotype"
    habitat = "Habitat"
    paragraph = "Paragraph"
    title = "Title"


class SearchEntity:
    def __init__(self, annotation_id: str, type: EntityType, word: str):
        self.id = annotation_id
        self.type = type
        self.word = word


class SynonymType(Enum):
    exact = "EXACT"
    related = "RELATED"


class Synonym:
    def __init__(self, type: SynonymType, word: str):
        self.type = type
        self.word = word


class Biotope:
    def __init__(self, onto_id=-1, name="", synonyms: List[Synonym] = None, is_as: List[str] = None):
        if synonyms is None:
            synonyms = []
        if is_as is None:
            is_as = []

        self.id = onto_id
        self.name = name
        self.synonyms = synonyms
        self.is_as = is_as
