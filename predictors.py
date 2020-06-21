from typing import Dict

import tensorflow as tf

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
        context_sim, surface_sim, name_sim = 0, 0, 0

        if len(term.context_embedding.tensor.shape) != 0:
            context_sim = cos_sim(se_sentence_embed, term.context_embedding)

        if len(term.surface_embedding.tensor.shape) != 0:
            surface_sim = cos_sim(se_name_embed, term.surface_embedding)

        if len(term.name_embedding.tensor.shape) != 0:
            name_sim = cos_sim(se_name_embed, term.name_embedding)

        if surface_sim < 0.1:
            name_surface_avg = name_sim
        else:
            name_surface_avg = 0.4 * surface_sim + 0.6 * name_sim

        if context_sim == 0:
            local_sim = 0.15 + .75 * name_surface_avg
        else:
            local_sim = 0.25 * context_sim + 0.75 * name_surface_avg

        if local_sim > best_sim and local_sim > .5:
            best_cos_sims = [context_sim, surface_sim, name_sim]
            best_sim = local_sim
            predicted_term = term_key

    print(f"{search_entity.name}\tscore:{best_cos_sims}\tprediction:{predicted_term}")

    return Prediction(search_entity.id, predicted_term, search_entity.type, best_sim)
