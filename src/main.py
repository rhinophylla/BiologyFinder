'''
This script implements BiologyFinder, a program that identifies biologists whose work is similar to a user-specified biologist on the basis of shared reference history.  The progam also generates a recommended reading list of scientific articles relavent to the subfield of the specified biologist.
'''
import numpy as np
import pandas as pd
from Bio import Entrez
from Bio import Medline
from sklearn.metrics import jaccard_similarity_score
from scipy.stats import pearsonr
import biologyfinder_fxn as bffxn
import logging

# Set up logging
# Create custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
ch = logging.StreamHandler()
fh = logging.FileHandler('BiologyFinder_results.log', mode='w')
ch.setLevel(logging.INFO)
fh.setLevel(logging.INFO)

# Create formatters and add to handlers
c_format = logging.Formatter('%(message)s')
f_format = logging.Formatter('%(message)s')
ch.setFormatter(c_format)
fh.setFormatter(f_format)

logger.addHandler(ch)
logger.addHandler(fh)

logger.info("As this script runs, it will print status updates and key analysis points to the console as well as save them in a log file called BiologyFinder_results.log for future reference. \n")

# PubMed credentials
Entrez.email = ""
Entrez.api_key = ""

# Obtains name and affiliation of the biologist of interest
name, affiliation = bffxn.user_entered_info()
logger.info("This run of BiologyFinder will identify biologists who do work similar to {} and provide a recommended reading list for papers relevant to {}'s subfield.\n ".format(name, name))

# Retrieves papers authored by the biologist of interest
id_list, webenv, query_key = bffxn.get_scientist_papers(name, affiliation)

# User specifies up to 3 papers authored by the biologist of interest on which to base this BiologyFinder session
chosen_papers = bffxn.user_selected_papers(id_list, webenv, query_key)
logger.info("The BiologyFinder analysis will be based on the following papers: \n")
bffxn.get_citations(chosen_papers, logger)
logger.info("\n")

# Creates master list of biologists from the first and last authors of papers referenced by the selected papers or cited by the selected papers
master_biologist_list = bffxn.create_master_biologist_list(chosen_papers, logger)
logger.info("\n")
logger.info("The master list contains {} biologists.\n".format(len(master_biologist_list)))

# Stores the papers authored by each of the biologists on the master list
logger.info("\n")
the_biologist_paper_dict = bffxn.create_biologist_paper_dict(master_biologist_list, logger)
logger.info("\n")

# Stores all the papers referenced by each of the biologists on the master list
the_biologist_cited_papers_dict = bffxn.create_biologist_cited_papers_dict(the_biologist_paper_dict, logger)

# Assembles every paper referenced by any of the biologists into one list
the_paper_features_list = bffxn.create_paper_features_list(the_biologist_cited_papers_dict)
logger.info("\n")
logger.info("The paper features list contains {} papers. \n".format(len(the_paper_features_list)))

# Creates binary vectors for each biologist indicating if they reference or do not reference each paper in the_paper_features_list
logger.info("Creating binary feature vectors for each biologist.\n")
the_binary_feature_vectors = bffxn.create_binary_feature_vectors(the_biologist_cited_papers_dict, the_paper_features_list)

# Creates a binary vector indicating if the original papers reference or do not reference each paper in the_paper_features_list
logger.info("Creating the comparison vector using the original 3 papers.\n")
the_comparision_binary_vector = bffxn.create_comparison_binary_vector(chosen_papers, the_paper_features_list, logger)

# Turns all the binary feature vectors into a dataframe
logger.info("Creating a dataframe to hold the biologist feature vectors.\n")
bf_df = bffxn.create_biologist_finder_df(the_binary_feature_vectors, the_paper_features_list, the_biologist_cited_papers_dict, the_comparision_binary_vector)
logger.info("Dataframe has {} rows and {} columns.\n".format(bf_df.shape[0], bf_df.shape[1]))

# Creates a sorted dataframe reporting the pearsonr score between the feature vector of each scientist and that of the original papers
logger.info("Creating a dataframe to hold similarity scores of each biologist.\n")
ss_df = bffxn.create_similarity_scores_df(bf_df)

# Prints the user-specified percentage of biologists whose reference history is closest to that of the original biologist as approximated by the references in the selected papers
user_percent = float(input("For which percentage of the master list of biologists do you want similarity scores reported for? Please enter a decimal.  For example for 20%, enter .2  "))
top_sim_bio_df = bffxn.most_sim_biologists(ss_df, user_percent)
logger.info("Biologists with the highest similarity scores: \n")
logger.info(top_sim_bio_df)

# Prints a reading list of a user-specified number of papers that are the most cited by the list of similar biologists created in the previous step.
logger.info("Generating reading list.\n")
bffxn.reading_list(bf_df, top_sim_bio_df, logger)
