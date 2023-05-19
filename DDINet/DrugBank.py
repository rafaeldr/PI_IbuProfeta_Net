import xmltodict
import pandas as pd
import collections

silent = False          # Display track of progress info (when False)

class DrugBank:

    drugbank_dict = []
    df_drugs = []
    df_drugsSynonyms = []
    df_interactions = []
    version = ""

    def __init__(self, drugbank_file, version = ""):
        self.drugbank_file = drugbank_file
        self.version = version
        self.__importSourceFile()

    def __importSourceFile(self):
        # Importing Data Sources (AS-IS) - DrugBank
        if not silent: print('Importing Data Sources (AS-IS) - DrugBank') 
        with open(self.drugbank_file, encoding='utf-8') as fd:
            self.drugbank_dict = xmltodict.parse(fd.read())
    
    def preProcess(self):
        self.__processDrugs()
        self.__processInteractions()
        self.__validation()

    def __processDrugs(self):
        # Drugs - Extraction
        if not silent: print('DrugBank - Extracting Names') 
        data = []
        dataSynonyms = []
        for drug in self.drugbank_dict['drugbank']['drug']:
            if type(drug['drugbank-id']) == list:
                id = str(drug['drugbank-id'][0]['#text'])
            else:
                id = str(drug['drugbank-id']['#text'])
            id = id[2:] # Adjust ID to integer (not varchar/string)
            data.append({'drugbank-id':int(id),
                         'name':str(drug['name']).strip().upper()
                         })

            # Drugs - Synonyms
            if drug['synonyms']!=None:
                if type(drug['synonyms']['synonym']) == collections.OrderedDict: # only 1 registry
                    synonymName = str(drug['synonyms']['synonym']['#text']).strip().upper()
                    dataSynonyms.append({'drugbank-id':int(id),
                                 'name':synonymName
                                 })
                elif type(drug['synonyms']['synonym']) == list:
                    for synonym in drug['synonyms']['synonym']:
                        synonymName = str(synonym['#text']).strip().upper()
                        dataSynonyms.append({'drugbank-id':int(id),
                                     'name':synonymName
                                     })
                else:
                    print('Unexpected error: Unexpected condition during DrugBank Synonyms extraction.')
                    exit(1)

        self.df_drugs = pd.DataFrame(data)
        self.df_drugsSynonyms = pd.DataFrame(dataSynonyms)

    def __processInteractions(self):
        # Interactions - Extraction
        if not silent: print('DrugBank - Extracting Interactions') 
        data = []
        for drugOrigin in self.drugbank_dict['drugbank']['drug']:
            if type(drugOrigin['drugbank-id']) == list:
                drugOrigin_id = str(drugOrigin['drugbank-id'][0]['#text'])
            else:
                drugOrigin_id = str(drugOrigin['drugbank-id']['#text'])

            if drugOrigin['drug-interactions']!=None:
                if type(drugOrigin['drug-interactions']['drug-interaction']) == collections.OrderedDict: # only 1 registry
                    drugDestiny_id = str(drugOrigin['drug-interactions']['drug-interaction']['drugbank-id'])
                    data.append([int(drugOrigin_id[2:]),
                                 int(drugDestiny_id[2:])
                                 ])
        # Changed for execution time improvement
        #            data.append({'drugbank-id1':drugOrigin_id,
        #                         'drugbank-id2':drugDestiny_id})
                elif type(drugOrigin['drug-interactions']['drug-interaction']) == list:
                    for drugDestiny in drugOrigin['drug-interactions']['drug-interaction']:
                        drugDestiny_id = str(drugDestiny['drugbank-id'])
                        data.append([int(drugOrigin_id[2:]),
                                     int(drugDestiny_id[2:])
                                     ])
                else:
                    print('Unexpected error: Unexpected condition during DrugBank drug-interaction extraction.')
                    exit(1)

        # Removing reversed duplicates
        if not silent: print('DrugBank - Interactions - Removing Reversed Duplicates') 
        data = {tuple(sorted(item)) for item in data}
        self.df_interactions = pd.DataFrame(data, columns=['drugbank-id1','drugbank-id2'])

        # Test Constraint id1 < id2 always
        if sum(self.df_interactions['drugbank-id1']<self.df_interactions['drugbank-id2']) != len(self.df_interactions):
            print("Unexpected error: DrugBank interactions should respect 'id1 < id2'.")
            exit(1)

    def __validation(self):
        # Check Referential Integrity
        diff_set = set(set(self.df_interactions['drugbank-id1']).union(self.df_interactions['drugbank-id2'])).difference(self.df_drugs['drugbank-id'])
        if len(diff_set) > 0:
            if not silent: print('Warning: Found '+str(len(diff_set))+' DrugBank ids that do not respect referential integrity.')
            if not silent: print('         These are '+str(diff_set)[1:-1]+'.')
            if not silent: print('         Trying to force the inclusion of these ids!')
            if not silent: print('         An extra computing power that could be avoided.')
    
            # Force Adjustments
            found = len(diff_set)
            counter = 0
            for drugOrigin in self.drugbank_dict['drugbank']['drug']:
                if drugOrigin['drug-interactions']!=None:
                    if drugOrigin['drug-interactions']['drug-interaction'] == collections.OrderedDict: # only 1 registry
                        drugDestiny_id = str(drugOrigin['drug-interactions']['drug-interaction']['drugbank-id'])
                        drugDestiny_id = int(drugDestiny_id[2:])
                        if drugDestiny_id in diff_set:
                            drugDestiny_name = str(drugOrigin['drug-interactions']['drug-interaction']['name'])
                            self.df_drugs = self.df_drugs.append({'drugbank-id': drugDestiny_id, 'name': drugDestiny_name.strip().upper()}, ignore_index=True)
                            diff_set.remove(drugDestiny_id)
                            counter += 1
                    elif type(drugOrigin['drug-interactions']['drug-interaction']) == list:
                        for drugDestiny in drugOrigin['drug-interactions']['drug-interaction']:
                            drugDestiny_id = str(drugDestiny['drugbank-id'])
                            drugDestiny_id = int(drugDestiny_id[2:])
                            if drugDestiny_id in diff_set:
                                drugDestiny_name = str(drugDestiny['name'])
                                self.df_drugs = self.df_drugs.append({'drugbank-id': drugDestiny_id, 'name': drugDestiny_name.strip().upper()}, ignore_index=True)
                                diff_set.remove(drugDestiny_id)
                                counter += 1
    
            if counter<found or len(diff_set)>0:
                print("Unexpected error: Some ids referenced by interactions don't exist as DrugBank drug names.")
                exit(1)
    
        # DrugBank Drug Synonyms (Concat)
        self.df_drugsSynonyms = pd.concat([self.df_drugs, self.df_drugsSynonyms], ignore_index=True)
        self.df_drugsSynonyms = self.df_drugsSynonyms.drop_duplicates()
        self.df_drugsSynonyms.reset_index(inplace=True, drop=True)

        # Validation: Unicity of Names 
        # (does not guarantee semantic unicity)
        if len(self.df_drugs['name']) != len(set(self.df_drugs['name'])):
            print("Unexpected error: DrugBank Names are not unique!")
            exit(1)


    def export(self):
        # Exporting
        if not silent: print('DrugBank - Exporting CSVs') 
        #base_exp_path = r"..\Exported\exp_"+self.version
        base_exp_path = r"..\Exported\DrugBank\exp_"+self.version
        self.df_drugs.to_csv(base_exp_path+"_drugs.csv", index = False)
        self.df_drugsSynonyms.to_csv(base_exp_path+"_drugsSynonyms.csv", index = False)
        self.df_interactions.to_csv(base_exp_path+"_interactions.csv", header = False, index = False)
        self.edgelistfile = base_exp_path+"_interactions.csv"