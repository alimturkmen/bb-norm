from typing import List, Dict

import tensorflow as tf
from tqdm import tqdm
from transformers import TFAutoModel, AutoTokenizer

from entity import Biotope
from utility import load_pkl


class ContextEmbedding(object):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("monologg/biobert_v1.1_pubmed")
        self.model = TFAutoModel.from_pretrained("monologg/biobert_v1.1_pubmed", from_pt=True)
        self.w2v_dic = load_pkl('w2v.pkl')

    def sentence_embed(self, sentences: List[str]):
        embed_list = []
        for sentence in sentences:
            input_ids = tf.constant(self.tokenizer.encode(sentence))[None, :]  # Batch size 1
            out, _ = self.model(input_ids)
            embed_list.append(out[-1][-1])
        return embed_list

    def name_embed(self, name: str):
        name = name.lower()
        if name in self.w2v_dic:
            return tf.convert_to_tensor(self.w2v_dic[name])
        else:
            tensor_list = []
            n_list = name.split(' ')
            for token in n_list:
                if token in self.w2v_dic:
                    tensor_list.append(tf.convert_to_tensor(self.w2v_dic[token]))
                else:
                    sub_tokens = token.split('-')
                    for sub_token in sub_tokens:
                        if sub_token in self.w2v_dic:
                            tensor_list.append(tf.convert_to_tensor(self.w2v_dic[sub_token]))
                        else:
                            continue  # print(f"unknown token: {sub_token}")

            return tf.reduce_sum(tf.convert_to_tensor(tensor_list), axis=0)

    def biotope_embed(self, biotopes: Dict[str, Biotope]) -> Dict[str, Biotope]:

        with tqdm(total=len(biotopes)) as pbar:
            for biotope in biotopes:

                sentences = biotopes[biotope].sentences
                embed_list = self.sentence_embed(sentences)
                avg_embed = tf.math.reduce_mean(tf.convert_to_tensor(embed_list), axis=0)
                biotopes[biotope].context_embedding = avg_embed

                surfaces = biotopes[biotope].surfaces
                # surface_embeds = self.sentence_embed(surfaces)
                surface_embeds = []
                for s in surfaces:
                        embed = self.name_embed(s.lower())
                        if len(embed.shape) == 0:
                            continue
                        surface_embeds.append(embed)
                avg_surf_embed = tf.math.reduce_mean(tf.convert_to_tensor(surface_embeds), axis=0)
                biotopes[biotope].surface_embedding = avg_surf_embed

                name = biotopes[biotope].name
                name_embed = self.name_embed(name)
                # name_embed = tf.convert_to_tensor(self.sentence_embed([name]))
                biotopes[biotope].name_embedding = name_embed

                synonyms_embeds = []
                for synonym in biotopes[biotope].synonyms:
                    embed = self.name_embed(synonym.name.lower())
                    if len(embed.shape) == 0:
                        continue
                    synonyms_embeds.append(embed)

                avg_synonym_embed = tf.math.reduce_mean(tf.convert_to_tensor(synonyms_embeds), axis=0)

                biotopes[biotope].synonym_embedding = avg_synonym_embed

                is_as_embeds = []
                for is_a in biotopes[biotope].is_as:
                    embed = self.name_embed(biotopes[is_a].name.lower())
                    if len(embed.shape) == 0:
                        continue
                    is_as_embeds.append(embed)

                avg_is_a_embed = tf.math.reduce_mean(tf.convert_to_tensor(is_as_embeds), axis=0)
                biotopes[biotope].is_a_embedding = avg_is_a_embed

                pbar.update(1)

        return biotopes

    def update_biotope_embed(self, biotopes: Dict[str, Biotope]) -> Dict[str, Biotope]:
        with tqdm(total=len(biotopes)) as pbar:
            for biotope in biotopes:

                sentences = biotopes[biotope].sentences
                embed_list = self.sentence_embed(sentences)
                avg_embed = tf.math.reduce_mean(tf.convert_to_tensor(embed_list), axis=0)
                biotopes[biotope].context_embedding = avg_embed

                surfaces = biotopes[biotope].surfaces
                # surface_embeds = self.sentence_embed(surfaces)
                surface_embeds = []
                for s in surfaces:
                    embed = self.name_embed(s.lower())
                    if embed.shape == []: continue
                    surface_embeds.append(embed)
                avg_surf_embed = tf.math.reduce_mean(tf.convert_to_tensor(surface_embeds), axis=0)
                biotopes[biotope].surface_embedding = avg_surf_embed

                pbar.update(1)

        return biotopes
