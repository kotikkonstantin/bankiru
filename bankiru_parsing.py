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



