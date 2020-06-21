import math
from enum import Enum
from glob import glob
from typing import List

import tensorflow as tf


class EntityType(Enum):
    phenotype = "Phenotype"
    habitat = "Habitat"
    microorganism = "Microorganism"


class SynonymType(Enum):
    exact = "EXACT"
    related = "RELATED"


class BiotopeContext:
    def __init__(self, annotation_id: str, sentence: str, type: EntityType, index: int):
        self.sentence = sentence
        self.index = index
        self.type = type
        self.id = annotation_id
        self.biotope_ids = []

    def add_biotope_id(self, biotope_id: str):
        self.biotope_ids.append(biotope_id)


class BiotopeFeatures:
    def __init__(self, surf: str, sent: str):
        self.surfaces = [surf]
        self.sentences = [sent]

    def add_surface(self, surf: str):
        self.surfaces.append(surf)

    def add_sentence(self, sent: str):
        self.sentences.append(sent)


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
        if annotation_id in self.entities:
            self.entities[annotation_id].append(term_id)
        else:
            self.entities[annotation_id] = [term_id]


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
        self.sentences = []
        self.surfaces = []
        self.context_embedding = None
        self.surface_embedding = None
        self.name_embedding = None
        self.is_a_embedding = None
        self.synonym_embedding = None

    def add_context(self, bio_features: BiotopeFeatures):
        self.sentences += bio_features.sentences
        self.surfaces += bio_features.surfaces


class Prediction:
    def __init__(self, annotation_id: str, predicted_term_id: str, term_type: EntityType, confidence: float):
        self.annotation_id = annotation_id
        self.predicted_term_id = predicted_term_id
        self.term_type = term_type
        self.confidence = confidence

    def print(self):
        term_type = "NCBI_Taxonomy Annotation:" if self.term_type == EntityType.microorganism else "OntoBiotope Annotation:"
        referent = "Referent:" if self.term_type == EntityType.microorganism else "Referent:OBT:"
        return "{}{} {}{}".format(term_type, self.annotation_id, referent, self.predicted_term_id)


class DataSet:
    def __init__(self, train_set_dir: str):
        self.txt_files = sorted(glob(train_set_dir + "*.txt"))
        self.a1_files = sorted(glob(train_set_dir + "*.a1"))
        self.a2_files = sorted(glob(train_set_dir + "*.a2"))


class EmbedCache:
    def __init__(self, tensor: tf.Tensor):
        self.tensor = tensor
        self.length = math.sqrt(tf.reduce_sum(tensor * tensor))


class BiotopeCache:
    def __init__(self, name: str, context_embedding: EmbedCache, surface_embedding: EmbedCache,
                 name_embedding: EmbedCache, is_a_embedding: EmbedCache, synonym_embedding: EmbedCache):
        self.name = name
        self.context_embedding = context_embedding
        self.surface_embedding = surface_embedding
        self.name_embedding = name_embedding
        self.is_a_embedding = is_a_embedding
        self.synonym_embedding = synonym_embedding
