### Goals
New biologists entering a subfield are often overwhelmed by the amount of preexisting literature that they need to sort through to get up to speed.  A Nature article from 2016 stated that 1 million articles are indexed by PubMed each year which means that on average, 2 papers a minute are added to the database.  While a new graduate student or an established researcher exploring a new subfield can certainly read a few review articles as an initial attempt to survey the field, the tool presented here is an alternative way to discover scientists of interest and to pare down the literature into a list of essential reading.

### Creating the biologist-article database

"BiologyFinder" is a tool aimed at new biology graduate students or postdoctoral researchers who have just joined a lab and are looking to understand the research of the lab.  It is written in Python and relies on the Python library, Bioython, to interact with NCBI's PubMed, a biology literature database.  The user enters the name of the lab head and optionally, the biologist's institutional affiliation.  The program then retrieves all the biologist's papers from PubMed and has the user select up to three of them.  These three papers form the originating body of work and they are used to identify scientists doing related work and to generate a list of "recommended reading" for the subfield. These recommendations are based on shared citations.  Next, the program retrieves all the papers cited within the original 3 papers as well as any paper that cited any of the original three papers.  The program then retrieves all the first and last authors of this collection of papers.  Only the first and last authors are used because this tool is aimed at biologists and generally, the first author is the student or postdoc who did the bulk of the research while the last author is the person whose lab in which the research was completed.  This list of authors represents the master list of biologists working in the field that the biologist recommendations will be drawn from.

Next, all the papers written by the master list of biologists are retrieved from PubMed as well as all the papers cited within those papers.  The cited papers become the paper features list and make up the pool of papers potentially relevant to the field.  The program then considers the master biologist list and the paper feature list and generates a dataframe where the biologists' names are rows and the paper features are columns.  A 1 is entered into the dataframe if the biologist has cited the paper and a 0 is entered if they did not.  This creates a binary feature vector associated with each scientist. Finally, a feature vector for the originating body of work called "comparison" is generated in the same way and added to the dataframe.


### The biologist recommendation engine

To determine which biologists on the master biologist list cite papers similar to the originating body of work, the distance between the comparison feature vector and those of the other biologists is calculated using the Pearson correlation coefficient. The master list of biologists is sorted from most to least similar to the originating body of work and the user can then input which percentage of the master biologist list length they want to be returned.  For example, if the user chooses 10% and the master list of biologists is 200 biologists long, then the 20 biologists with the highest similarity scores are returned.

### Generating a list of recommended reading

To generate a list of required reading, the feature vector database is filtered to only include the biologists on the "most similar" list previously generated. The program then sums up the number of times each paper was cited at least once by a biologist on the most similar list and sorts the papers by how often they are cited.  The program returns the number of papers cited by 10%, 20%, 30% ... up to 100%  of the most similar biologists then asks the user to specify how many papers they want on their recommended reading list. The program then returns a formatted reference for the specified number of papers.  The papers are listed from most to least cited.

### BiologyFinder examples

As a proof of principle, I used my BiologyFinder tool to generate a list of scientists similar to Carolyn G. Rasmussen, a plant cell biologist at the University of California Riverside and a list of recommended reading relevant to her subfield. From her list of published work, I chose the following papers to be the originating body of work:

1. Predicting Division Planes of Three-Dimensional Cells by Soap-Film Minimization. 'Martinez P', 'Allsman LA', 'Brakke KA', 'Hoyt C', 'Hayes J', 'Liang H', 'Neher W', 'Rui Y', 'Roberts AM', 'Moradifam A', 'Goldstein B', 'Anderson CT', 'Rasmussen CG'. The Plant cell. 2018 Oct. (30150312)
2. Division Plane Orientation Defects Revealed by a Synthetic Double Mutant Phenotype. 'Mir R', 'Morris VH', 'Buschmann H', 'Rasmussen CG'. Plant physiology. 2018 Jan. (29146775)
3. Proper division plane orientation and mitotic progression together allow normal growth of maize. 'Martinez P', 'Luo A', 'Sylvester A', 'Rasmussen CG'. Proceedings of the National Academy of Sciences of the United States of America. 2017 Mar 7. (28202734)

These three papers referenced or were referenced by 157 different papers which were written by 237 unique first or last authors.  These 237 authors form the master biologist list.  Scientists with these names wrote a total of XXX papers which referenced a total of 137,462 unique papers.  Whether or not a biologist cited each of these 137,462 papers generates the feature vector for each biologist.  The comparison feature vector, the papers cited in the original 3 papers authored by Dr. Rassmussen was created and compared to the other 237. Each scientist was assigned a similarity score and then the scientists were ordered by their similarity scores.  20% of the scientists with the highest similarity scores are listed below.

similarity               Scientist
1.000000                comparison
0.681091       Rasmussen, Carolyn G
0.413291               Mir, Ricardo
0.338864          Buschmann, Henrik
0.293337            Martinez, Pablo
5      0.207184           Asada, Tetsuhiro
169    0.198325                   Rui, Yue
121    0.191691           Lipka, Elisabeth
212    0.174955            Walker, Keely L
90     0.141453            Herrmann, Arvid
125    0.137144           Louveaux, Marion
196    0.136276          Stockle, Dorothee
2      0.131331        Anderson, Charles T
156    0.120293         Pastuglia, Martine
146    0.119744           Moukhtar, Julien
180    0.114898          Schaefer, Estelle
117    0.112803          Lee, Yuh-Ru Julie
70     0.108854             Goldstein, Bob
109    0.105179              Kirik, Viktor
205    0.104973          Van Damme, Daniel
214    0.098086      Wasteneys, Geoffrey O
77     0.097577            Hamant, Olivier
187    0.097452              Shao, Wanchen
191    0.097427            Smith, Laurie G
113    0.096667              Komis, George
27     0.093372           Boudaoud, Arezki
143    0.091199           Mirabet, Vincent
26     0.090838             Bouchez, David
147    0.089675             Mulder, Bela M
30     0.086663          Bringmann, Martin
47     0.081828                 Dixit, Ram
148    0.081437             Muller, Sabine
123    0.080888             Lloyd, Clive W
115    0.079825           Landrein, Benoit
195    0.073703              Spinner, Lara
39     0.071606                Chan, Jordi
149    0.069822            Murata, Takashi
63     0.069717                Furutani, I
49     0.068815            Dumais, Jacques
224    0.067522                Wu, Shu-Zon
24     0.064053              Boruc, Joanna
176    0.060563               Samaj, Jozef
45     0.059192               Cyr, Richard
107    0.058809        Kierzkowski, Daniel
228    0.058130         Yuen, Christen Y L
151    0.057844        Nakamura, Masayoshi
100    0.056518  Jaquez-Gutierrez, Marybel



The top entry, "comparison" represents the originating body of work compared to itself which is why it has a similarity score of 1.  Dr. Rasumssen herself is on the list because she cites her work and she is thus included in the master list of 237 biologists.  Reassuringly, her overall citation profile is similar to the citation profile of her three paper subset.

Looking at the list more generally, several top matches are trainees (Ricardo Mir and Pablo Martinez) or collaborators (Henrik Buschmann) of Dr. Rasmussen.  Since they co-author papers together, it is not surprising that they have a similar citation history.  I showed the list to Dr. Rasmussen and she thought it was representative of biologists who work on her field.

Finally, the program identifies papers that are cited by the most similar group of biologists.  Below is the report the program provided before asking the user how many papers they want in their recommended reading list.

636 papers were cited at least once by 10% (4) of the most similar biologists
160 papers were cited at least once by 20% (9) of the most similar biologists
78 papers were cited at least once by 30% (13) of the most similar biologists
25 papers were cited at least once by 40% (18) of the most similar biologists
9 papers were cited at least once by 50% (23) of the most similar biologists
2 papers were cited at least once by 60% (27) of the most similar biologists
1 papers were cited at least once by 70% (32) of the most similar biologists
0 papers were cited at least once by 80% (36) of the most similar biologists
0 papers were cited at least once by 90% (41) of the most similar biologists
0 papers were cited at least once by 100% (46) of the most similar biologists

Given this information, I asked the program to return the references for 9 papers.  These 9 papers were cited by at least 50% of the most similar scientists and were returned in order from most cited to least.

1. Floral dip: a simplified method for Agrobacterium-mediated transformation of Arabidopsis thaliana. ['Clough SJ', 'Bent AF']. The Plant journal: for cell and molecular biology. 1998 Dec. (10069079)
2. Sustained microtubule treadmilling in Arabidopsis cortical arrays. ['Shaw SL', 'Kamyar R', 'Ehrhardt DW']. Science (New York, N.Y.). 2003 Jun 13. (12714675)
3. Visualization of cellulose synthase demonstrates functional association with microtubules. ['Paredez AR', 'Somerville CR', 'Ehrhardt DW']. Science (New York, N.Y.). 2006 Jun 9. (16627697)
4. Organization of microtubules and endoplasmic reticulum during mitosis and cytokinesis in wheat meristems. ['Pickett-Heaps JD', 'Northcote DH']. Journal of cell science. 1966 Mar. (5929804)
5. Microtubule and katanin-dependent dynamics of microtubule nucleation complexes in the acentrosomal Arabidopsis cortical array. ['Nakamura M', 'Ehrhardt DW', 'Hashimoto T']. Nature cell biology. 2010 Nov. (20935636)
6. The Arabidopsis TONNEAU2 gene encodes a putative novel protein phosphatase 2A regulatory subunit essential for the control of the cortical cytoskeleton. ['Camilleri C', 'Azimzadeh J', 'Pastuglia M', 'Bellini C', 'Grandjean O', 'Bouchez D']. The Plant cell. 2002 Apr. (11971138)
7. MOR1 is essential for organizing cortical microtubules in plants. ['Whittington AT', 'Vugrek O', 'Wei KJ', 'Hasenbein NG', 'Sugimoto K', 'Rashbrooke MC', 'Wasteneys GO']. Nature. 2001 May 31. (11385579)
8. The Arabidopsis CLASP gene encodes a microtubule-associated protein involved in cell expansion and division. ['Ambrose JC', 'Shoji T', 'Kotzer AM', 'Pighin JA', 'Wasteneys GO']. The Plant cell. 2007 Sep. (17873093)
9. A katanin-like protein regulates normal cell wall biosynthesis and cell elongation. ['Burk DH', 'Liu B', 'Zhong R', 'Morrison WH', 'Ye ZH']. The Plant cell. 2001 Apr. (11283338)

The first paper is a widely cited plant methods paper, but the remaining 8 are important works within Dr. Rasmussen's subfield.

Finally, I repeated the analysis using Dr. Ian Tietjen, an HIV researcher.  I only used 2 papers as the originating body of work and after I shared the results with him, he responded "...everyone on the list below Raymond Andersen are definitely people I know who do work similar to mine, and that I cite frequently. There are definitely gaps in that list, but these people are plenty to get started with.  The 32 papers that you brought up are largely pretty big ones too...".  This suggests that this tool might be useful to a wide variety of biologists.

### Problems with this approach

1.  One of the major issues is that PubMed does not provide a reference list for every paper it indexes.  This is problematic if when selecting the initial 3 papers of interest, one or more of them do not contain the reference list and you have to go with another perhaps less relevant option or only use 1-2 papers.  It can also skew the results later if some important papers are not included in the feature vector or if some scientists only cite them in papers where references are not included.
2.  The recommended reading list is heavily weighted towards classic papers and those published in the more distant past.  This is because the older a paper is, the more time there has been for it to be cited.

### Previous work
This project was inspired by a tool presented within the K2 Data Science boot camp that discovers new GitHub repositories based on a shared "starring" history.

### Future work
Future improvements for this tool include:

### References
Landhuis, E. Scientific literature: Information overload. Nature 535, 457–458 (2016) doi:10.1038/nj7612-457a
