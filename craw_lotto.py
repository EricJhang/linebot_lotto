from bs4 import BeautifulSoup
import requests
import pandas as pd
import psycopg2
import os
DATABASE_URL = os.environ['DATABASE_URL']
head_Html='http://www.taiwanlottery.com.tw/Lotto/Lotto649/history.aspx'
header_Item_name_list_lotto = ['期別','開獎日','兌獎截止','銷售金額','獎金總額']
header_Id_List_lotto = ['Lotto649Control_history_dlQuery_L649_DrawTerm_','Lotto649Control_history_dlQuery_L649_DDate_','Lotto649Control_history_dlQuery_L649_EDate_','Lotto649Control_history_dlQuery_L649_SellAmount_','Lotto649Control_history_dlQuery_Total_']
winning_Numbers_title_List_lotto = ['獎號1','獎號2','獎號3','獎號4','獎號5','獎號6','特別號']
winning_Numbers_Id_lotto = ['Lotto649Control_history_dlQuery_SNo1_','Lotto649Control_history_dlQuery_SNo2_','Lotto649Control_history_dlQuery_SNo3_','Lotto649Control_history_dlQuery_SNo4_','Lotto649Control_history_dlQuery_SNo5_','Lotto649Control_history_dlQuery_SNo6_','Lotto649Control_history_dlQuery_No7_']
winning_Numbers_Sort_lotto = ['Lotto649Control_history_dlQuery_No1_','Lotto649Control_history_dlQuery_No2_','Lotto649Control_history_dlQuery_No3_','Lotto649Control_history_dlQuery_No4_','Lotto649Control_history_dlQuery_No5_','Lotto649Control_history_dlQuery_No6_','Lotto649Control_history_dlQuery_SNo_']

header_Id_List_SuperLotto = ['SuperLotto638Control_history1_dlQuery_DrawTerm_','SuperLotto638Control_history1_dlQuery_Date_','SuperLotto638Control_history1_dlQuery_EDate_','SuperLotto638Control_history1_dlQuery_SellAmount_','SuperLotto638Control_history1_dlQuery_Total_']


winning_Numbers_Sort_SuperLotto = ['SuperLotto638Control_history1_dlQuery_No1_','SuperLotto638Control_history1_dlQuery_No2_','SuperLotto638Control_history1_dlQuery_No3_','SuperLotto638Control_history1_dlQuery_No4_','SuperLotto638Control_history1_dlQuery_No5_','SuperLotto638Control_history1_dlQuery_No6_','SuperLotto638Control_history1_dlQuery_No7_']

yearly_list = ['107','106']
monthly_list_107 = ['5','4','3','2','1']
monthly_list_106 = ['12','11','10','9','8','7','6','5','4','3','2','1']
monthly_list = ['5','4','3','2','1']
monthly= '3'
VIEWSTATE =""
EVENTVALIDATION=""
search_type_kind = ['lotto','superlotto']
header_Id_List = []
winning_Numbers_Sort = []
def find_viewstata_evet(res):
    id_list=["__VIEWSTATE","__EVENTVALIDATION"]
    soup = BeautifulSoup(res,'lxml')
    tmp_result = soup.find(id=id_list[0])
    tmp_result_2 = soup.find(id=id_list[1])
    print(tmp_result_2)
    return tmp_result['value'],tmp_result_2['value']
    
def craw_lotto_info(search_type):
    global header_Id_List,winning_Numbers_Sort
    head_Html_lotto='http://www.taiwanlottery.com.tw/Lotto/Lotto649/history.aspx'
    head_Html_superlotto='http://www.taiwanlottery.com.tw/lotto/superlotto638/history.aspx'
    if(search_type == search_type_kind[0]):
        head_Html = head_Html_lotto
        header_Id_List = header_Id_List_lotto
        winning_Numbers_Id = winning_Numbers_Id_lotto
        winning_Numbers_Sort = winning_Numbers_Sort_lotto
    elif(search_type == search_type_kind[1]):
        head_Html = head_Html_superlotto
        header_Id_List = header_Id_List_SuperLotto
        winning_Numbers_Sort = winning_Numbers_Sort_SuperLotto
        winning_Numbers_Id = winning_Numbers_Sort_SuperLotto
    r2 = get_html(head_Html)
    soup2 = BeautifulSoup(r2,'lxml')
    #print(soup2.prettify())
    header_Info = soup2.find_all(id=search_header_info)
    header_Info_List = []
    header_Info_Dict = {}
    header_Info_List,header_Info_Dict = parse_tw_lotto_html(header_Info,[],{},header_Id_List)
    winning_Numbers_Info = soup2.find_all(id=search_winning_numbers)
    date_list = list(header_Info_Dict.keys())
    winning_Numbers_List,winning_Numbers_Dict = parse_tw_lotto_html(winning_Numbers_Info,[],{},winning_Numbers_Id,date_list)
    return header_Info_Dict,winning_Numbers_Dict
    
        
def search_header_info(css_class):
    global header_Id_List 
    if(css_class != None):
        for i in range(len(header_Id_List)):
            if header_Id_List[i] in css_class:
                return css_class            
def search_winning_numbers(css_class):
    global winning_Numbers_Sort
    if(css_class != None):
        for i in range(len(winning_Numbers_Sort )):
            if winning_Numbers_Sort [i] in css_class:
                return css_class                
def get_html(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return " ERROR " 
def parse_tw_lotto_html(data_Info,data_Info_List,data_Info_Dict,data_Id_List,date_list = None):  
    for index  in range(len(data_Info)) :
        if (index == 0):
            data_Info_List.append(data_Info[index].text)  
        else:
            if(index % len(data_Id_List) != 0):
                data_Info_List.append(data_Info[index].text)
            else:
                if(date_list != None):
                    #print(int(index /len(data_Id_List)))
                    print(len(date_list))
                    print(len(data_Info))
                    data_Info_Dict[date_list[int(index /len(data_Id_List))-1]] = list(data_Info_List)
                else:
                    data_Info_Dict[data_Info[index-len(data_Id_List)].text] = list(data_Info_List)
                data_Info_List= []
                data_Info_List.append(data_Info[index].text)
    if(date_list != None):          
        data_Info_Dict[date_list[-1]] = list(data_Info_List)
    else:
        data_Info_Dict[data_Info[len(data_Info)-len(data_Id_List)].text] = list(data_Info_List)
    return data_Info_List,data_Info_Dict  

    