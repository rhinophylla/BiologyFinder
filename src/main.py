'''
This script implements BiologyFinder, a program that identifies biologists whose work is similar to a user provided biologist.  The progam also generates a recommended reading list of scientific articles relavent to the subfield of the provided biologist.
'''
import numpy as np
import pandas as pd
from Bio import Entrez
from Bio import Medline
from sklearn.metrics import jaccard_similarity_score
from scipy.stats import pearsonr
import src.biologyfinder_fxn as bffxn

Entrez.email = "ajwright@gmail.com"
Entrez.api_key = "86ac8038bfc913213f007df2803127ebc908"

name, affliation = user_entered_info(bffxn.user_entered_info)
print(name, affliation)

id_list, webenv, query_key = get_scientist_papers(name, affiliation)

chosen_papers = user_selected_papers(id_list, webenv, query_key)
print(chosen_papers)

master_biologist_list = create_master_biologist_list(chosen_papers)

the_biologist_paper_dict = create_biologist_paper_dict(master_biologist_list)

the_biologist_cited_papers_dict = create_biologist_cited_papers_dict(the_biologist_paper_dict)

the_paper_features_list = create_paper_features_list(the_biologist_cited_papers_dict)

the_binary_feature_vectors = create_binary_feature_vectors(the_biologist_cited_papers_dict, the_paper_features_list)

the_comparision_binary_vector = create_comparison_binary_vector(chosen_papers, the_paper_features_list)

bf_df = create_biologist_finder_df(the_binary_feature_vectors, the_paper_features_list, the_biologist_cited_papers_dict, the_comparision_binary_vector, name)

print(bf_df.shape)
print(bf_df.head())
print(bf_df.tail())

#from fastparquet import write
#write('Rasmussen_ver3_df.parq',bf_df)
