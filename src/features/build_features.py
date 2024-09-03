import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def build_features(input_filepath_users, input_filepath_caract, input_filepath_places, input_filepath_veh, output_folderpath):
    # Importing datasets
    df_users = pd.read_csv(input_filepath_users, sep=";")
    df_caract = pd.read_csv(input_filepath_caract, sep=";", header=0, low_memory=False)
    df_places = pd.read_csv(input_filepath_places, sep=";", encoding='utf-8')
    df_veh = pd.read_csv(input_filepath_veh, sep=";")

    # Creating new columns
    nb_victim = pd.crosstab(df_users.Num_Acc, "count").reset_index()
    nb_vehicules = pd.crosstab(df_veh.Num_Acc, "count").reset_index()
    df_users["year_acc"] = df_users["Num_Acc"].astype(str).apply(lambda x : x[:4]).astype(int)
    df_users["victim_age"] = df_users["year_acc"] - df_users["an_nais"]
    df_users.loc[(df_users["victim_age"] > 120) | (df_users["victim_age"] < 0), "victim_age"] = np.nan
    df_caract["hour"] = df_caract["hrmn"].astype(str).apply(lambda x : x[:-3])
    df_caract.drop(['hrmn', 'an'], inplace=True, axis=1)
    df_users.drop(['an_nais'], inplace=True, axis=1)

    # Replacing names
    df_users.grav.replace([1,2,3,4], [1,3,4,2], inplace=True)
    df_caract.rename({"agg" : "agg_"}, inplace=True, axis=1)
    df_caract["dep"] = df_caract["dep"].replace({"2A":"201", "2B":"202"})
    df_caract["com"] = df_caract["com"].replace({"2A":"201", "2B":"202"})

    # Converting columns types
    df_caract[["dep","com", "hour"]] = df_caract[["dep","com", "hour"]].astype(int)
    df_caract["lat"] = df_caract["lat"].str.replace(',', '.').astype(float)
    df_caract["long"] = df_caract["long"].str.replace(',', '.').astype(float)

    # Grouping modalities
    df_caract["atm"] = df_caract["atm"].replace({1:0, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:0, 9:0})
    catv_value = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,30,31,32,33,34,35,36,37,38,39,40,41,42,43,50,60,80,99]
    catv_value_new = [0,1,1,2,1,1,6,2,5,5,5,5,5,4,4,4,4,4,3,3,4,4,1,1,1,1,1,6,6,3,3,3,3,1,1,1,1,1,0,0]
    df_veh['catv'] = df_veh['catv'].replace(dict(zip(catv_value, catv_value_new)))

    # Merging datasets
    fusion1 = df_users.merge(df_veh, on=["Num_Acc","num_veh", "id_vehicule"], how="inner")
    fusion1 = fusion1.sort_values(by="grav", ascending=False).drop_duplicates(subset=['Num_Acc'], keep="first")
    fusion2 = fusion1.merge(df_places, on="Num_Acc", how="left")
    df = fusion2.merge(df_caract, on='Num_Acc', how="left")

    # Adding new columns
    df = df.merge(nb_victim, on="Num_Acc", how="inner").rename(columns={"count":"nb_victim"})
    df = df.merge(nb_vehicules, on="Num_Acc", how="inner").rename(columns={"count":"nb_vehicules"})

    # Modification of the target variable : 1 : prioritary // 0 : non-prioritary
    df['grav'] = df['grav'].replace({2:0, 3:1, 4:1})

    # Replacing values -1 and 0
    col_to_replace0_na = ["trajet", "catv", "motor"]
    col_to_replace1_na = ["trajet", "secu1", "catv", "obsm", "motor", "circ", "surf", "situ", "vma", "atm", "col"]
    df[col_to_replace1_na] = df[col_to_replace1_na].replace(-1, np.nan)
    df[col_to_replace0_na] = df[col_to_replace0_na].replace(0, np.nan)

    # Dropping columns
    list_to_drop = ['senc','larrout','actp', 'manv', 'choc', 'nbv', 'prof', 'plan', 'Num_Acc', 'id_vehicule', 'num_veh', 'pr', 'pr
