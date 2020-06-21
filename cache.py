#! /usr/bin/env python
import sys

import tensorflow as tf
from tqdm import tqdm

import defs
from context_embedding import ContextEmbedding
from context_parser import find_a1_file_context, find_all_biotope_contexts
from entity import DataSet, EmbedCache, BiotopeCache
from utility import save_pkl


def run(save_dir):
    train_set = DataSet(defs.TRAIN_PATH)
    dev_set = DataSet(defs.DEV_PATH)
    test_set = DataSet(defs.TEST_PATH)

    context_embedding = ContextEmbedding()

    # Structures as follows Dict[file_name, Dict[search_entity.id, EmbedCache]]
    sentence_embeds = {}
    name_embeds = {}

    # Structures as follows Dict[term_id, BiotopeCache]
    biotope_embeds = {}

    # If you want to cache other sets, change the data_set to it/them
    data_set = test_set
    with tqdm(total=len(data_set.a1_files)) as pbar:
        for i in range(len(data_set.a1_files)):
            file_name = data_set.a1_files[i].split('/')[-1][0:-3]

            sentence_embeds[file_name] = {}
            name_embeds[file_name] = {}

            search_entities_context = find_a1_file_context(data_set.a1_files[i], data_set.txt_files[i])

            for search_entity_context_key in search_entities_context:
                name_embed_cache = EmbedCache(context_embedding.name_embed(search_entity_context_key))

                for search_entity in search_entities_context[search_entity_context_key]:
                    sentence_embed_cache = EmbedCache(
                        tf.convert_to_tensor(context_embedding.sentence_embed([search_entity.sentence]))
                    )

                    name_embeds[file_name][search_entity.id] = name_embed_cache
                    sentence_embeds[file_name][search_entity.id] = sentence_embed_cache

            pbar.update(1)

    # Save the cache
    save_pkl(sentence_embeds, save_dir + "test_sentence_embeds.pkl")
    save_pkl(name_embeds, save_dir + "test_name_embeds.pkl")

    # Train contexts with dev + train
    data_set = dev_set
    data_set.a1_files += train_set.a1_files
    data_set.a2_files += train_set.a2_files
    data_set.txt_files += train_set.txt_files

    biotopes_contexts = find_all_biotope_contexts(data_set, defs.ONTOBIOTOPE_FILE_PATH)
    biotopes_contexts = context_embedding.biotope_embed(biotopes_contexts)

    # Save the cache
    save_pkl(biotopes_contexts, save_dir + "biotope_contexts.pkl")

    for key in biotopes_contexts:
        if biotopes_contexts[key].context_embedding is not None:
            context_embed_cache = EmbedCache(biotopes_contexts[key].context_embedding)
        else:
            context_embed_cache = None

        if biotopes_contexts[key].surface_embedding is not None:
            surface_embed_cache = EmbedCache(biotopes_contexts[key].surface_embedding)
        else:
            surface_embed_cache = None

        if biotopes_contexts[key].name_embedding is not None:
            name_embed_cache = EmbedCache(biotopes_contexts[key].name_embedding)
        else:
            name_embed_cache = None

        if biotopes_contexts[key].synonym_embedding is not None:
            synonym_embed_cache = EmbedCache(biotopes_contexts[key].synonym_embedding)
        else:
            synonym_embed_cache = None

        if biotopes_contexts[key].is_a_embedding is not None:
            is_a_embed_cache = EmbedCache(biotopes_contexts[key].is_a_embedding)
        else:
            is_a_embed_cache = None

        biotope_embeds[key] = BiotopeCache(biotopes_contexts[key].name, context_embed_cache,
                                           surface_embed_cache,
                                           name_embed_cache, synonym_embed_cache, is_a_embed_cache)

    # Save the cache
    save_pkl(biotope_embeds, save_dir + "biotope_embeds.pkl")


if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 2:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    _save_dir = sys.argv[1]

    run(_save_dir)
