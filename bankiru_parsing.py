# Парсинг банковских рейтингов с сайта banki.ru / Parsing bank ratings from site banki.ru

import requests
import re
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd

def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text)) # очень крутые регулярные выражения - убирают все скобочки, тэги и прочую ерунду

def bank_names_and_lics(ratings_page):
    num_lics = []
    bank_names = []

    for cont in ratings_page.findAll('div', attrs = {'class':"b-bank-name"}):
        name, num = re.split('No.|,', html_stripper(cont))[:2]
        num_lics += [num]
        bank_names += [name]

    num_lics = list(map(int,num_lics))
    
    return (num_lics, bank_names)

# Вишенка на тортике. Функция, делающая всё:) / The func, which does all necessary.

def bankiru_parsing(pages_number: int, verbose = False):
    """
    return: DataFrame table corresponding banki.ru table
    """
    main_url = "http://www.banki.ru/banks/ratings/agency/?PAGEN_2={}&mode=2"
    
    ratings = pd.DataFrame()
    
    #unique moodys values, just lists of constants 
    s_MOODYS = ["P-1","P-2","P-3","NP","отозван"]

    on_nat_MOODYS = ["Aaa.ru","Aa1.ru","Aa2.ru","Aa3.ru","A1.ru","A2.ru","A3.ru",                "Baa1.ru","Baa2.ru","Baa3.ru","Ba1.ru","Ba2.ru","Ba3.ru","B1.ru",                 "B2.ru","B3.ru","Caa1.ru","Caa2.ru","Caa3.ru","Ca.ru","C.ru",                    "отозван"]

    fin_stab_MOODYS = ["A","B+","B","B-","C+","C","C-","D+","D","D-","E+","E","E-","отозван"]

    for page in range(1, pages_number+1):
        
        if verbose:
            print(page)
        ratings_page = requests.get(main_url.format(page))
        ratings_page = ratings_page.content
        ratings_page = BeautifulSoup(ratings_page, "lxml")
    
        sp=re.split('<td>|</td>', str(ratings_page.findAll('div', attrs = {"class":"b-table-ratings"})).replace('\n', ' ').replace("<!--","").replace("-->","").replace('[',"").replace(']',""))
        sp = list(map(html_stripper, sp))
        sp = [el for el in sp if len(el.split())!= 0]
    
        
        flag = 1
        new_line = None
        bank_ind = 0
        num_lics = bank_names_and_lics(ratings_page)[0] 
        bank_names = bank_names_and_lics(ratings_page)[1]
        for i in range(len(sp)):    
            l = sp[i].split()[:4]
            if flag:
                new_line = dict()
                flag=0
        
            if "Moody's" in l:
                if "Рус-рейтинг" in sp[i+1].split()[:4]:
                    new_line["l_in_foreign_MOODYS"] = np.nan
                    new_line["l_in_nat_MOODYS"] = np.nan
                    new_line["MOODYS"] = np.nan
                    new_line["s_in_foreign_MOODYS"] = np.nan
                    new_line["s_in_nat_MOODYS"] = np.nan
                    new_line["on_nat_MOODYS"] = np.nan
                    new_line["fin_stab_MOODYS"] = np.nan
                    new_line["dates_MOODYS"] = np.nan
                elif len(l) == 1: #special code for 2312 num lic
                    new_line["l_in_foreign_MOODYS"] = np.nan
                    new_line["l_in_nat_MOODYS"] = np.nan
                    new_line["MOODYS"] = np.nan
                    new_line["s_in_foreign_MOODYS"] = np.nan
                    new_line["s_in_nat_MOODYS"] = np.nan
                    if sp[i+1].split()[:4][0] in on_nat_MOODYS:
                        if len(sp[i+1].split()[:4][0]) == 10:
                            new_line["on_nat_MOODYS"] = np.nan
                        else:
                            new_line["on_nat_MOODYS"] = sp[i+1].split()[:4][0]
                    
                    new_line["fin_stab_MOODYS"] = np.nan

                    if len(sp[i+2].split()[:4][0]) == 10:
                        new_line["dates_MOODYS"] = sp[i+2].split()[:4][0]
                else:
                    
                    new_line["l_in_foreign_MOODYS"] = l[1]
                    new_line["l_in_nat_MOODYS"] = l[2]
                    new_line["MOODYS"] = l[3]

                    if sp[i+1].split()[:2][0] in s_MOODYS:
                        new_line["s_in_foreign_MOODYS"] = sp[i+1].split()[:4][0]
            
                    if sp[i+1].split()[:2][1] in s_MOODYS:
                        new_line["s_in_nat_MOODYS"] = sp[i+1].split()[:4][1]
            
                    if sp[i+2].split()[:4][0] in on_nat_MOODYS:
                        if len(sp[i+3].split()[:4][0]) == 10:
                            new_line["on_nat_MOODYS"] = np.nan
                        else:
                            new_line["on_nat_MOODYS"] = sp[i+2].split()[:4][0]
                    
                    if sp[i+2].split()[:4][0] in fin_stab_MOODYS: 
                        new_line["fin_stab_MOODYS"] = sp[i+2].split()[:4][0]
                
                    elif len(sp[i+2].split()[:4][0]) == 10:
                        new_line["dates_MOODYS"] = sp[i+2].split()[:4][0]
                
                    if sp[i+3].split()[:4][0] in fin_stab_MOODYS: 
                        new_line["fin_stab_MOODYS"] = sp[i+3].split()[:4][0]
                
                    elif len(sp[i+3].split()[:4][0]) == 10:
                        new_line["dates_MOODYS"] = sp[i+3].split()[:4][0]
            
                    if len(sp[i+4].split()[:4][0]) == 10:
                        new_line["dates_MOODYS"] = sp[i+4].split()[:4][0]
                        
            if "Эксперт" in l:
                if "НРА" in sp[i+1].split()[:4]:
                    new_line["EXPERT_RA"] = np.nan
                    new_line["EXPERT_RA_prognosis"] = np.nan
                    new_line["EXPERT_RA_dates"] = np.nan
                else:
                    new_line["EXPERT_RA"] = sp[i+1].split()[:4][0]
                    if new_line["EXPERT_RA"] == sp[i+1].split()[:4][1]:
                        new_line["EXPERT_RA_prognosis"] = np.nan
                    else:
                        new_line["EXPERT_RA_prognosis"] = sp[i+1].split()[:4][1]
            
                    new_line["EXPERT_RA_dates"] = sp[i+2].split()[:4][0]
            
            if "НРА" in l:
                if 'AK&M' in sp[i+1].split()[:4]:
                    new_line["НРА"] = np.nan
                    new_line["НРА_prognosis"] = np.nan
                    new_line["НРА_dates"] = np.nan
                else:
                    new_line["НРА"] = sp[i+1].split()[:4][0]
                    if new_line["НРА"] == sp[i+1].split()[:4][1]:
                        new_line["НРА_prognosis"]= np.nan
                    else:
                        new_line["НРА_prognosis"] = sp[i+1].split()[:4][1]
                
                    new_line["НРА_dates"] = sp[i+2].split()[:4][0]
            
            if "AK&M" in l:
                try:
                    if "Moody's" in sp[i+1].split()[:4]:
                        new_line["AK&M"] = np.nan
                        new_line["AK&M_prognosis"] = np.nan
                        new_line["AK&M_dates"] = np.nan
            
                    else:
                        new_line["AK&M"] = sp[i+1].split()[:4][0]
                        if new_line["AK&M"] == sp[i+1].split()[:4][1]:
                            new_line["AK&M_prognosis"]= np.nan
                        else:
                            new_line["AK&M_prognosis"] = sp[i+1].split()[:4][1]
                
                        new_line["AK&M_dates"] = sp[i+2].split()[:4][0]
                except:
                    new_line["AK&M"] = np.nan
                    new_line["AK&M_prognosis"] = np.nan
                    new_line["AK&M_dates"] = np.nan    
        
                flag = 1
        
            if flag:
                new_line["num_of_lic"] = num_lics[bank_ind]
                new_line["bank_name"] = bank_names[bank_ind]
                ratings = ratings.append(new_line, ignore_index=True)
                bank_ind += 1
                flag = 0 

    ratings = ratings[["num_of_lic", "bank_name","l_in_foreign_MOODYS","l_in_nat_MOODYS", "MOODYS", "s_in_foreign_MOODYS", "s_in_nat_MOODYS", "on_nat_MOODYS", "fin_stab_MOODYS", "dates_MOODYS", "EXPERT_RA", "EXPERT_RA_prognosis","EXPERT_RA_dates","НРА","НРА_prognosis", "НРА_dates","AK&M","AK&M_prognosis","AK&M_dates"]]

    return ratings


# На сайте banki.ru есть 11 страниц таблицы с рейтингами о банках / In banki.ru there are 11 table pages with ratings of banks.

data=bankiru_parsing(pages_number = 11)

# Преобразование значений признаков к числовому формату / Transformation features to numeric format
# (see **расшифровка-признаков-в-рейтингах-банков.docx** for understanding)

data["num_of_lic"] = data["num_of_lic"].astype("str").astype(float).astype(int) 

#Preprocessing of "l_in_foreign_MOODYS"
data["l_in_foreign_MOODYS"] = data["l_in_foreign_MOODYS"].astype("str")
data["l_in_foreign_MOODYS"].replace(to_replace = ["C","Ca","Caa3","Caa2","Caa1","B3","B2","B1", "Ba3", "Ba2", "Ba1", "Baa3","Baa2", "Baa1", "A3","A2","A1", "Aa3", "Aa2", "Aa1", "Aaa", "nan"], value = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,np.nan], inplace = True)
#Values of Series are set in numeric except value "nan", which will be NaN
data["l_in_foreign_MOODYS"] = pd.to_numeric(data["l_in_foreign_MOODYS"], errors="coerce")

#Preprocessing of "l_in_nat_MOODYS"
data["l_in_nat_MOODYS"] = data["l_in_nat_MOODYS"].astype("str")
data["l_in_nat_MOODYS"].replace(to_replace = ["C","Ca","Caa3","Caa2","Caa1","B3","B2","B1", "Ba3", "Ba2", "Ba1", "Baa3","Baa2", "Baa1", "A3","A2","A1", "Aa3", "Aa2", "Aa1", "Aaa", "nan"], value = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,np.nan], inplace = True)
#Values of Series are set in numeric except value "nan", which will be NaN
data["l_in_nat_MOODYS"] = pd.to_numeric(data["l_in_nat_MOODYS"], errors="coerce")

#Preprocessing of "MOODYS"
data["MOODYS"] = data["MOODYS"].astype("str")
data["MOODYS"].replace(to_replace = ['негативный', 'стабильный', 'позитивный'], value = [0,1,2], inplace = True)
#Values of Series are set in numeric except value nan, which will be NaN
data["MOODYS"] = pd.to_numeric(data["MOODYS"], errors="coerce")

#Preprocessing of "s_in_foreign_MOODYS"
data["s_in_foreign_MOODYS"].replace(to_replace = ['NP','P-3','P-2','P-1', "отозван"], value = [0,1,2,3,-1], inplace = True)

#Preprocessing of "s_in_nat_MOODYS"
data["s_in_nat_MOODYS"].replace(to_replace = ['NP','P-3','P-2','P-1', "отозван"], value = [0,1,2,3,-1], inplace = True)

#Preprocessing of "on_nat_MOODYS"
data["on_nat_MOODYS"] = data["on_nat_MOODYS"].astype("str")
#Values of Series are set in numeric except "nan" and trully string vars, which will be NaN
data["on_nat_MOODYS"] = pd.to_numeric(data["on_nat_MOODYS"], errors="coerce")

#Preprocessing of "fin_stab_MOODYS" 
data["fin_stab_MOODYS"] = data["fin_stab_MOODYS"].astype("str")
data["fin_stab_MOODYS"].replace(to_replace = ['E-', 'E', 'E+', "D-","D","D+", "C-","C", "C+", "B-", "B", "B+", "A"],value =[0,1,2,3,4,5,6,7,8,9,10,11,12], inplace = True)
#Values of Series are set in numeric except value "nan", which will be NaN
data["fin_stab_MOODYS"] = pd.to_numeric(data["fin_stab_MOODYS"], errors="coerce")

#Preprocessing of "EXPERT_RA"
data["EXPERT_RA"] = data["EXPERT_RA"].astype("str")
data["EXPERT_RA"].replace(to_replace = "-2", value = '-1', inplace = True)
#providing same format
data["EXPERT_RA"].replace(to_replace = ['D', 'RD', "C", "CC", "CCC","B-", "B", "B+", "BB-", "BB", "BB+", "BBB-", "BBB", "BBB+", "A-", "A", "A+", "AA-", "AA", "AA+", "AAA", "C++", "B++", "A++"], value = ['ruD', 'ruRD', "ruC", "ruCC", "ruCCC","ruB-", "ruB", "ruB+",                  "ruBB-", "ruBB", "ruBB+", "ruBBB-", "ruBBB", "ruBBB+", "ruA-", "ruA", "ruA+", "ruAA-", "ruAA", "ruAA+", "ruAAA", "ruCCC", "ruBB-", "ruAA-"], inplace = True)
data["EXPERT_RA"].replace(to_replace = ['ruD', 'ruRD', "ruC", "ruCC", "ruCCC","ruB-", "ruB", "ruB+", "ruBB-","ruBB", "ruBB+", "ruBBB-", "ruBBB", "ruBBB+", "ruA-", "ruA", "ruA+", "ruAA-", "ruAA", "ruAA+", "ruAAA"], value = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], inplace = True)

#Values of Series are set in numeric except value "nan", which will be NaN
data["EXPERT_RA"] = pd.to_numeric(data["EXPERT_RA"], errors="coerce")

#Preprocessing of "EXPERT_RA_prognosis"
data["EXPERT_RA_prognosis"] = data["EXPERT_RA_prognosis"].astype("str")
data["EXPERT_RA_prognosis"].replace(to_replace = ['негативный', 'стабильный', 'позитивный'], value = [0,1,2], inplace = True)
#Values of Series are set in numeric except value nan, which will be nan
data["EXPERT_RA_prognosis"] = pd.to_numeric(data["EXPERT_RA_prognosis"], errors="coerce")


# ### Preprocessing of "EXPERT_RA_prognosis"
data["NRA"] = data["NRA"].astype("str")
data["NRA"].replace(to_replace = "-2", value = '-1', inplace = True)
data["NRA"].replace(to_replace = ['D', 'C-', "C", "C+","CC-", "CC", "CC+", "B-", "B", "B+", "BB-","BB", "BB+", "BBB-", "BBB", "BBB+", "A-", "A", "A+", "AA-", "AA", "AA+", "AAA"], value = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22], inplace = True)
#Values of Series are set in numeric except value "nan", which will be NaN
data["NRA"] = pd.to_numeric(data["NRA"], errors="coerce")


#Preprocessing of "NRA_prognosis"
data["NRA_prognosis"] = data["NRA_prognosis"].astype("str")
data["NRA_prognosis"].replace(to_replace = ['негативный', 'стабильный', 'позитивный'], value = [0,1,2], inplace = True)
#Values of Series are set in numeric except value nan, which will be nan
data["NRA_prognosis"] = pd.to_numeric(data["NRA_prognosis"], errors="coerce")

#Preprocessing of "AK&M"
data["AK&M"] = data["AK&M"].astype("str")
data["AK&M"].replace(to_replace = "-2", value = '-1', inplace = True)
data["AK&M"].replace(to_replace = ['D', 'C', "C+","C++", "B", "B+", "B++", "A", "A+", "A++"], value = [0,1,2,3,4,5,6,7,8,9], inplace = True)
#Values of Series are set in numeric except value "nan", which will be NaN
data["AK&M"] = pd.to_numeric(data["AK&M"], errors="coerce")

#Preprocessing of "AK&M_prognosis"
data["AK&M_prognosis"] = data["AK&M_prognosis"].astype("str")
data["AK&M_prognosis"].replace(to_replace = ['негативный', 'стабильный', 'позитивный'], value = [0,1,2], inplace = True)

#Values of Series are set in numeric except value nan, which will be nan
data["AK&M_prognosis"] = pd.to_numeric(data["AK&M_prognosis"], errors="coerce")



