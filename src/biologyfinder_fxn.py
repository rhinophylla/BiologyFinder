import numpy as np
import pandas as pd
from Bio import Entrez
from Bio import Medline
from scipy.stats import pearsonr
import logging


def user_entered_info():
    """Stores user-provided scientist name and affiliation.

    Arguments:
    none

    Returns:
    name - str; scientist name in the format "firstname middleinit lastname"
    affiliation - str; scientist's institutional affiliation
    """
    print("Type the answer to each question then press return.  If you do not know the answer, just hit return.")
    first_name = input("What is the first name of the scientist of interest? ")
    middle_name = input("What is the middle initial of the scientist of interest? ")
    try:
        middle_initial = middle_name[0]
    except IndexError:
        middle_initial = ""
    last_name = input("What is the last name of the scientist of interest? ")
    affliation = input("What is the affiliation of the scientist of interest? No abbreviations, please. ")
    name = "{0} {1} {2}".format(first_name.lower(), middle_initial.lower(), last_name.lower())
    return name, affliation


def get_scientist_papers(name, affiliation=None):
    """Searches PubMed for papers whose author list and affiliation list contain the provided author name and affiliation.

    Arguments:
    name - str; complete scientist name in the format "lastname, firstname middleinitial"
    affiliation (optional) - str

    Returns:
    ids - list; list of paper IDs
    webenv - str; used to reference cached NCBI search session in future efetch queries
    query_key - str; used to reference cached NCBI search session in future efetch queries
    """
    if affiliation == None:
        handle = Entrez.esearch(db='pubmed', term=name, retmax=200, usehistory="y")
    else:
        terms = "{} AND {}".format(name, affiliation)
        handle = Entrez.esearch(db='pubmed', term=terms, retmax=200, usehistory="y")
    record = Entrez.read(handle)
    ids = record['IdList']
    webenv = record["WebEnv"]
    query_key = record["QueryKey"]
    return ids, webenv, query_key


def user_selected_papers(id_list, webenv, query_key):
    """Allows the user to select up to 3 papers authored by a scientist of interest. Uses NCBI cached search history.

    Arguments:
    id_list - list; paper ids
    webenv - str; used to reference cached NCBI search session in efetch queries
    query_key - str; used to reference cached NCBI search session in efetch queries

    Returns
    select_list - list; paper ids of user selected papers
    """
    from Bio import Medline
    print("Please select up to 3 papers by keying in the corresponding number(s). Seperate each number by a comma.")
    handle = Entrez.efetch(db="pubmed", id=id_list, rettype='medline', retmode='text', webenv=webenv, query_key=query_key)
    records = Medline.parse(handle)
    for index, record in enumerate(records, 1):
        print("{}. {} {}. {}. {}. ({})".format(index, record.get("TI", "?"), record.get("AU", "?"), record.get("JT", "?"), record.get("DP", "?"), record.get("PMID", "?")))
    paper_num = input("Which papers would you like to select? ")
    paper_num = paper_num.split(',')
    #print(paper_num)
    while paper_num == ['']:
        paper_num = input("No papers selected.  Please select up to 3 papers by keying in the corresponding number(s). Seperate each number by a comma.")
        paper_num = paper_num.split(',')
    while len(paper_num) > 4:
        paper_num = input("Too many papers selected.  Please select up to 3 papers by keying in the corresponding number(s). Seperate each number by a comma.")
        paper_num = paper_num.split(',')
    select_list = []
    for num in paper_num:
        select_list.append(id_list[int(num)-1])
    return select_list


def compile_refs_and_citedin(paper_list, logger):
    """Takes a list of paper IDs and returns a list of the IDs for papers referenced in the original paper list.  The reference list may be incomplete since PubMed does not provide references for all papers.

    Arguments:
    paper_list - list; paper IDs (str)

    Returns:
    pubmed_refs - list; paper IDs (str)
    """
    str_paper_list = ",".join(paper_list)
    search_results = Entrez.read(Entrez.epost("pubmed", id=str_paper_list))
    query_key = search_results["QueryKey"]
    webenv = search_results["WebEnv"]
    pub_records = Entrez.read(Entrez.elink(dbfrom="pubmed", WebEnv=webenv, query_key=query_key))
    ref_ids = []
    for entry in pub_records[0]["LinkSetDb"]:
        if entry["LinkName"] == 'pubmed_pubmed_refs':
            refs = entry["Link"]
            try:
                for ref in refs:
                    ref_ids.append(ref['Id'])
            except UnboundLocalError:
                logger.info("No references found")
        if entry["LinkName"] == 'pubmed_pubmed_citedin':
            cites = entry["Link"]
            try:
                for cite in cites:
                    ref_ids.append(cite['Id'])
            except UnboundLocalError:
                logger.info("No cited in found")
    #logger.info("Ref_ids list contains {} ids.".format(len(ref_ids)))
    #logger.info("After removing duplicates, the ", len(set(ref_ids)))
    return list(set(ref_ids))


def get_first_last_authors(paper_id):
    """Given a paper, returns the first and last authors of the paper.

    Arguments:
    paper_id - str; paper ids

    Returns:
    authors - list of strs; list of full names of the first and last authors of the provided paper id
    """
    handle = Entrez.efetch(db='pubmed', id=paper_id, rettype='medline', retmode="text", retmax=200)
    record = Medline.read(handle)
    authors = record.get("FAU", "?")
    first_last_authors = [authors[0], authors[-1]]
    return first_last_authors


def author_formatting(author_list):
    """Changes the formatting of author name strings to give the best PubMed search results.

    Arguments:
    author_list - list of str; list of author names

    Returns:
    formatted_author_list - list of str; alphabetized list of author names formatted "lastname, firstname"
    """
    formatted_author_list = []
    for author in author_list:
        #print(author)
        last_name = author.split(',')[0]
        first_name = author.split(',')[1].lstrip()
        try:
            if first_name[1] == " ":
                try:
                    first_name = first_name[0] + first_name[-1]
                except:
                    first_name = first_name[0]
        except:
            first_name = first_name[0]
        new_name = "{}, {}".format(last_name, first_name)
        #print(new_name)
        formatted_author_list.append(new_name)
    return sorted(formatted_author_list)


def remove_duplicates(sorted_list):
    """Takes a sorted list of authors and if 2 authors have the same last name and first initial, removes the name with only the first initial leaving behind the one that has the full first name.

    Arguments:
    sorted_list - list; alphabetized list of authors in the format "lastname, firstname middleinit" or "lastname, firstinit middleinit"

    Returns:
    author_no_dup_list - list; alphabetized list of authors with duplicates removed
    """
    author_no_dup_list = []
    most_recent_author = " , "
    for i, author in enumerate(sorted_list):
        if author.split(',')[0] == most_recent_author.split(',')[0]:
            if author.split(',')[1].lstrip()[0] != most_recent_author.split(',')[1].lstrip()[0]:
                author_no_dup_list.append(author)
                #print("(1) Compared {} to {} and appended {}".format(author, most_recent_author, author))
            else:
                #print("(2) Compared {} to {} and deleted {} and appended {}".format(author, most_recent_author, author_no_dup_list[-1], author))
                del author_no_dup_list[-1]
                author_no_dup_list.append(author)
        else:
            author_no_dup_list.append(author)
            #print("(3) Compared {} to {} and appended {}".format(author, most_recent_author, author))
        most_recent_author = author
    return author_no_dup_list


def create_master_biologist_list(paper_list, logger):
    """Searches PubMed for all the papers cited by or that cites a paper on the paper list.  Returns a list of the first and last authors of those papers (duplicates removed).

    Arguments:
    paper_list - list; paper IDs (str)

    Returns:
    biologist_master_list - list; biologist names (str)
    """
    ref_citedin_ids = compile_refs_and_citedin(paper_list, logger)
    first_last_author_list = []
    for paper in ref_citedin_ids:
        logger.info("Getting the authors of paper {}.".format(paper))
        authors = get_first_last_authors(paper)
        first_last_author_list.extend(authors)
    set_f_l_author_list = list(set(first_last_author_list))
    #print(len(set_f_l_author_list))
    format_f_l_author_list = author_formatting(set_f_l_author_list)
    #print(len(format_f_l_author_list))
    no_dup_f_l_author_list = remove_duplicates(format_f_l_author_list)
    #print(len(no_dup_f_l_author_list))
    return no_dup_f_l_author_list


def create_biologist_paper_dict(biologist_list, logger):
    """Takes a list of biologists and looks up the IDs of all the papers they authored in PubMed.  Returns a dictionary where the biologist's name is the key and the value is a list of their paper IDs.

    Arguments:
    biologist_list - list; biologist names (str)

    Returns:
    biologist_paper_dict - dict; keys are biologist names (str) and the values are a list of IDs of the papers authored by the biologist
    """
    biologist_papers_dict = {}
    for biologist in biologist_list:
        logger.info("Looking up papers authored by {}.".format(biologist))
        biologist_nocomma = biologist.replace(',', '')
        #logger.info("Getting papers authored by {}.".format(biologist_nocomma))
        papers = get_scientist_papers(biologist_nocomma)[0]
        biologist_papers_dict[biologist] = papers
    zero_papers = []
    has_papers = []
    total = 0
    for key, value in biologist_papers_dict.items():
        if len(value) == 0:
            zero_papers.append(key)
        else:
            has_papers.append(key)
        total += len(value)
    logger.info("The master list of biologists authored {} papers in the PubMed database.".format(total))
    logger.info("Zero papers were retrieved for the following authors: {}".format(zero_papers))
    logger.info("More than one paper was retrieved for the following authors: {}".format(has_papers))
    return biologist_papers_dict


def get_and_compile_refs(paper_list, logger):
    """Takes a list of paper IDs and returns a list of the IDs of the papers referenced by papers in the original list. The reference list may be incomplete since PubMed does not provide references for all papers.

    Arguments:
    paper_list - list, paper IDs (str)

    Returns:
    pubmed_refs - list, paper IDs
    """
    str_paper_list = ",".join(paper_list)
    search_results = Entrez.read(Entrez.epost("pubmed", id=str_paper_list))
    query_key = search_results["QueryKey"]
    webenv = search_results["WebEnv"]
    pub_records = Entrez.read(Entrez.elink(dbfrom="pubmed", WebEnv=webenv, query_key=query_key))
    for entry in pub_records[0]["LinkSetDb"]:
        if entry["LinkName"] == 'pubmed_pubmed_refs':
            pubmed_refs = entry["Link"]
    ref_ids = []
    try:
        for ref in pubmed_refs:
            ref_ids.append(ref['Id'])
    except UnboundLocalError:
        logger.info("No references found")
    return ref_ids


def create_biologist_cited_papers_dict(biologist_paper_dict, logger):
    """Takes a dictionary of biologists and the papers they wrote, looks up each paper in PubMed and returns a new dictionary containing the biologist and a list of all the papers they cite(reference) within the papers they wrote.

    Arguments:
    biologist_paper_dict - dict; keys are biologist's names (str) and the values are a list of IDs of the papers authored by the biologist

    Returns:
    biologist_cited_papers_dict - dict; keys are biologist's names (str) and the values are a list of IDS of papers cited by the biologist
    """
    biologist_cited_papers_dict = {}
    for key, value in biologist_paper_dict.items():
        logger.info("Looking up papers cited by {}.".format(key))
        try:
            paper_list = get_and_compile_refs(value, logger)
            biologist_cited_papers_dict[key] = paper_list
        except:
            biologist_cited_papers_dict[key] = []
    return biologist_cited_papers_dict


def create_paper_features_list(biologist_cited_papers_dict):
    """Takes a dictionary of cited papers and combines them into a list with no duplicates.

    Arguments:
    biologist_cited_papers_dict - dict; keys are biologist's names (str) and the values are a list of paper IDs cited in papers authored by the biologist

    Returns:
    paper_features - list; list of all the papers cited by every author in the starting dict (no duplicates)
    """
    paper_features_temp = []
    for value in biologist_cited_papers_dict.values():
        paper_features_temp.extend(value)
    paper_features = list(set(paper_features_temp))
    return paper_features


def create_binary_feature_vectors(biologist_cited_papers_dict, paper_features_list):
    """Builds a set of feature vectors for each biologist (key) in the biologist_cited_papers_dict by looking to see if each paper in the paper_feature_list is cited by the biologist (a list of cited papers is the value associated with each biologist key).  Adds a one to the feature vector if the paper is cited and a 0 if it is not.

    Arguments:
    biologist_cited_papers_dict - dict; keys are biologist's names (str) and the values are a list of paper IDs cited in papers authored by the biologist paper_features_list - list; list of all the papers cited by every author in the starting dict

    Returns:
    all_binary_feature_vectors - list of lists; lists of 1s and 0s that indicate if a biologist cited a paper in the paper_features_list or not
    """
    all_binary_feature_vectors = []
    for key, value in biologist_cited_papers_dict.items():
        biologist_vector = []
        for paper in paper_features_list:
            if paper in value:
                biologist_vector.append(1)
            else:
                biologist_vector.append(0)
        all_binary_feature_vectors.append(biologist_vector)
    return all_binary_feature_vectors


def create_comparison_binary_vector(paper_list, paper_features_list, logger):
    """Builds a feature vector for the originating set of papers by looking to see if each paper in the paper_features_list is cited by any of the originating set of papers. Adds a one to the feature vector if the paper is cited and a 0 if it is not.

    Arguments:
    paper_list - list; list of paper IDs (str) corresponding to the originating set of papers
    paper_features_list - list; list of all the papers cited by every author in the biologist_cited_papers_dict

    Returns:
    comparision_binary_vector - list; list of 1s and 0s that indicate if the originating set of papers cited a paper in the paper_features_list or not
    """
    comparison_binary_vector = []
    comparison_refs = get_and_compile_refs(paper_list, logger)
    for i in paper_features_list:
        if i in comparison_refs:
            comparison_binary_vector.append(1)
        else:
            comparison_binary_vector.append(0)
    return comparison_binary_vector


def create_biologist_finder_df(binary_feature_vectors, paper_features_list, biologist_cited_papers_dict, comparison_vector):
    """Takes the binary feature vectors and comparison binary vector and builds a pandas dataframe that has biologist's names as the index and paper IDs as the columns.  Dataframe is filled with 1s and 0s to indicate if a biologist has cited the column paper or not. The last row contains the data for the originating set of papers.

    Arguments:
    binary_feature_vectors - list of lists; lists of 0s and 1s that indicate if a biologist cited a paper in the paper_features_list
    paper_features_list - list; list of all the papers cited by every author in the starting dict
    biologist_cited_papers_dict - dict; keys are biologist names (str) and the values are a list of paper IDS corresponding to papers cited by the biologist
    comparison_vector - list; list of 0s and 1s that indicates if the originating set of papers cited a paper in the paper_features_list

    Returns:
    final_df - Pandas df; has biologist's names as the index and paper IDs as the columns.  Dataframe is filled with 1s and 0s to indicate if a biologist has cited the column paper or not. The last row represents the originating set of papers and is indexed as "comparison"
    """
    temp_df = pd.DataFrame(binary_feature_vectors, columns=paper_features_list, index=biologist_cited_papers_dict.keys())
    comp_series = pd.Series(comparison_vector).to_frame("comparison").T
    comp_series.columns = temp_df.columns
    final_df = pd.concat([temp_df, comp_series])
    final_df.dropna(axis=0, inplace=True)
    return final_df


def create_similarity_scores_df(biologist_finder_df):
    """Calculates pearsonr correlation coefficients between the last row of a dataframe and all the remaining rows. Reports the coefficient ("similarity") in a new dataframe with the same row index as the original dataframe.

    Arguments:
    biologist_finder_df - pandas dataframe; rows are individual feature vectors and the last row is compared to all other rows

    Returns:
    sorted_sim_df - pandas dataframe; 2 columns - "scientist" which is the biologist's name and "similarity" which is
    the pearsonr coefficient between the scientist's feature vector and the last row of biologist_finder_df.  Dataframe is sorted based on similarity scores from highest to lowest.
    """
    sim_score = {}
    for i in range(len(biologist_finder_df)):
        score = pearsonr(biologist_finder_df.iloc[-1, :], biologist_finder_df.iloc[i, :])
        sim_score.update({i: score[0]})
    sim_df = pd.Series(sim_score).to_frame("similarity")
    sim_df["Scientist"] = biologist_finder_df.index
    sorted_sim_df = sim_df.sort_values('similarity', ascending=False)
    return sorted_sim_df


def most_sim_biologists(similarity_df, per):
    """Takes a sorted dataframe and a float representing a percent.  Returns that percentage of the dataframe.

    Arguments:
    similarity_df - pandas dataframe; sorted dataframe
    per - float; represents a percentage

    Returns:
    similarity_df - pandas dataframe; truncated version of starting dataframe containing the user-specified percentage of rows
    """
    num_biologists = similarity_df.shape[0]
    top_per = int(num_biologists * per)
    similarity_df_per = similarity_df.head(top_per)
    #print(similarity_df_per)
    return similarity_df_per


def get_citations(rec_paper_list, logger):
    """Takes a list of paper ID numbers and return a PubMed reference for each paper on the list.

    Arguments:
    rec_paper_list - list of strs; paper IDs numbers

    Returns:
    None
    (prints the references to the screen)
    """
    id_list = ",".join(rec_paper_list)
    search_results = Entrez.read(Entrez.epost("pubmed", id=id_list))
    query_key = search_results["QueryKey"]
    webenv = search_results["WebEnv"]
    handle = Entrez.efetch(db="pubmed", id=id_list, rettype='medline', retmode='text', webenv=webenv, query_key=query_key)
    records = Medline.parse(handle)
    for index, record in enumerate(records, 1):
        logger.info("{}. {} {}. {}. {}. ({})".format(index, record.get("TI", "?"), record.get("AU", "?"), record.get("JT", "?"), record.get("DP", "?"), record.get("PMID", "?")))

def reading_list(biologist_finder_df, most_sim_bio_df, logger):
    """Takes a dataframe containing the most similar biologists as well as the binary feature vector dataframe. Creates a new dataframe with paper IDs as the index and biologists as columns and it contains a 1 if the biologist ever cited the paper and a 0 if not.  Citations per paper are summed and then the df is sorted so that the most cited papers are at the top.  Prints to the terminal the number of papers cited by 10%, 20%, 30%, etc of the most similar biologists.  Prints to the terminal citations for the user-specified number of papers.

    Arguments:
    biologist_finder_df - pandas dataframe; rows are individual biologist feature vectors
    most_sim_bio_df - pandas dataframe; 2 columns - "scientist" which is the biologist's name and "similarity" which is the pearsonr coefficient between scientist's feature vector and the last row of biologist_finder_df.

    Returns:
    None
    (prints to the terminal citations for a user-specified number of most cited papers)
    """
    top_per_biologists = list(most_sim_bio_df.iloc[1:, 1])
    num_top_biologists = len(top_per_biologists)
    most_cited_papers = biologist_finder_df.loc[top_per_biologists, :][biologist_finder_df.loc[top_per_biologists, :] ==1].fillna(0).T
    most_cited_papers['sum'] = most_cited_papers.sum(axis=1)
    most_cited_papers_sort = most_cited_papers.sort_values('sum', ascending=False)
    total_num_papers = most_cited_papers_sort.shape[0]
    for i in range(10, 110, 10):
        per_of_top_biol = round(num_top_biologists * i/100)
        num_papers = most_cited_papers_sort[most_cited_papers_sort["sum"] >= per_of_top_biol].shape[0]
        if num_papers != 1:
            logger.info("{} papers were cited at least once by {}% ({}) of the most similar biologists.".format(num_papers, i, per_of_top_biol))
        else:
            logger.info("{} paper was cited at least once by {}% ({}) of the most similar biologists.".format(num_papers, i, per_of_top_biol))
    num_papers = int(input("How many papers do you want on the recommended reading list? "))
    reading_list_ids = most_cited_papers_sort.head(num_papers).index.to_list()
    get_citations(reading_list_ids, logger)
