from typing import Dict

import tensorflow as tf
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from entity import Prediction, SearchEntity, EmbedCache, BiotopeCache


def cos_sim(embed1: EmbedCache, embed2: EmbedCache):
    dot_prod = tf.reduce_sum(embed1.tensor * embed2.tensor)
    return float(dot_prod / (embed1.length * embed2.length))


"""
    se prefix means search entity
"""


def context_predictor(search_entity: SearchEntity, se_sentence_embed: EmbedCache, se_name_embed: EmbedCache,
                      biotope_terms: Dict[str, BiotopeCache]) -> Prediction:
    # Set to root term as default
    predicted_term = '000000'

    best_cos_sims = []

    best_sim = 0
    for term_key in biotope_terms:
        term = biotope_terms[term_key]
        context_sim, surface_sim, _name_sim, syn_sim, is_a_sim = 0.65, 0, 0, 0, 0.65

        if len(term.context_embedding.tensor.shape) != 0:
            context_sim = max(cos_sim(se_sentence_embed, term.context_embedding), context_sim)
        
        if len(term.surface_embedding.tensor.shape) != 0:
            surface_sim = cos_sim(se_name_embed, term.surface_embedding)

        if len(term.name_embedding.tensor.shape) != 0:
            _name_sim = cos_sim(se_name_embed, term.name_embedding)

        if len(term.synonym_embedding.tensor.shape) != 0:
            syn_sim = cos_sim(se_name_embed, term.synonym_embedding)

        # if len(term.is_a_embedding.tensor.shape) != 0:
        #     is_a_sim = max(cos_sim(se_name_embed, term.is_a_embedding), is_a_sim)

        name_sim  = max(_name_sim, syn_sim)
        name_surface_avg  = max(name_sim, surface_sim)

        local_sim = 0.25*context_sim + 0.75*name_surface_avg #+ 0.05 *is_a_sim 


        if local_sim > best_sim:
            best_cos_sims = [context_sim, name_surface_avg]
            best_sim = local_sim
            predicted_term = term_key

    print(f"{search_entity.name}\tscore:{best_cos_sims}\tprediction:{predicted_term}")

    return Prediction(search_entity.id, predicted_term, search_entity.type, best_sim)
