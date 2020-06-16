from transformers import TFAutoModel, AutoTokenizer
import tensorflow as tf
import math
from typing import List, Dict
from entity import Biotope
from tqdm import tqdm

class ContextEmbedding(object):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("monologg/biobert_v1.1_pubmed")
        self.model = TFAutoModel.from_pretrained("monologg/biobert_v1.1_pubmed", from_pt=True)

    def sentence_embed(self, sentences:List[str]):
        embed_list = []
        for sentence in sentences:
            input_ids = tf.constant(self.tokenizer.encode(sentence))[None, :]  # Batch size 1
            out, _ = self.model(input_ids)
            embed_list.append(out[-1][-1])
        return embed_list

    def biotope_embed(self, biotopes:Dict[str, Biotope]) -> Dict[str, Biotope] :
        
        with tqdm(total=len(biotopes)) as pbar:
            for biotope in biotopes:

                sentences = biotopes[biotope].sentences
                embed_list = self.sentence_embed(sentences)
                avg_embed = tf.math.reduce_mean(tf.convert_to_tensor(embed_list), axis=0)
                biotopes[biotope].context_embedding = avg_embed
                '''
                surfaces = biotopes[biotope].surfaces
                surface_embeds = self.sentence_embed(surfaces)
                avg_surf_embed = tf.math.reduce_mean(tf.convert_to_tensor(surface_embeds), axis=0)
                biotopes[biotope].surface_embedding = avg_surf_embed
                '''
                pbar.update(1)
            
            
        return biotopes
