from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.options import Options
from get_mails_from_web import get_mails_from_web 

filename = "data"
link = "https://www.google.com/maps/search/boats+construction+companies+United+States/@40.7219,-110.0056348,4z?entry=ttu"


options = Options()
options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
browser = webdriver.Chrome(options=options)
record = []
e = []
le = 0 #esta variable contara el # de intentos de obtener resultados para cada pagination scroll que se haga
results_limit = 100

def Selenium_extractor():

    action = ActionChains(browser)
    #lista con los resultados de busqueda, los elementos con la clase "hfpxzc" son los links <a> que llevan al detalle de cada lugar
    a = browser.find_elements(By.CLASS_NAME, "hfpxzc") 

    print("Scrolling to capture search results ...")
    #con este bucle se hacen las paginaciones simulando el scroll del usuario 
    while len(a) < results_limit:
        var = len(a)
        #scroll hasta el ultimo resultado de busqueda
        scroll_origin = ScrollOrigin.from_element(a[len(a)-1]) 
        action.scroll_from_origin(scroll_origin, 0, 1000).perform()
        time.sleep(5)
        #se guarda en la lista "a" todos los resultados de busqueda existentes antes del scroll y despues
        a = browser.find_elements(By.CLASS_NAME, "hfpxzc")

        #numero de intentos de obtener resultados para cada paginacion
        if len(a) == var:
            le+=1
            if le > 10:
                break
        else:
            le = 0
            
    print("Scrapping info from each search results ...")
    for i in range(len(a)-1): #dejo el ultimo resultado de busqueda sin visitar para evitar dar click en el boton "go to top"
        try:
            #recupero el elemento i de la lista de resultados como un objeto de scroll
            scroll_origin = ScrollOrigin.from_element(a[i]) 
            #hago scroll hasta el elemento 
            action.scroll_from_origin(scroll_origin, 0, 100).perform()
            #muevo el mouse hasta el centro del elemento
            action.move_to_element(a[i]).perform()
            #hago click en el elemento
            a[i].click()
            time.sleep(2)
            source = browser.page_source
            soup = BeautifulSoup(source, 'html.parser')
            #nombre del sitio
            Name_Html = soup.findAll('h1', {"class": "DUwDvf lfPIob"})
            name = Name_Html[0].text
            if name not in e:
                #agrego el nombre del sitio 
                e.append(name)
                
                #extraigo los divs que contienen el resto de la info
                divs = soup.findAll('div', {"class": "Io6YTe fontBodyMedium kR99db"})
                #busco el telefono
                for j in range(len(divs)):
                    if str(divs[j].text)[0] == "+" or str(divs[j].text)[0] == "(":
                        phone = divs[j].text
                
                #address
                address=divs[0].text
                
                #busco el sitio web
                website = "Not available"
                try:
                    for z in range(len(divs)):
                        if str(divs[z].text)[-4] == "." or str(divs[z].text)[-3] == ".":
                            website = divs[z].text
                except:
                    website="Not available"
                
                #busco los mails del sitio web
                mails = tuple(get_mails_from_web(website))
                   
                print([name, phone, address, website, mails])
                record.append((name,phone,address,website,mails))
                df=pd.DataFrame(record,columns=['Name','Phone number','Address','Website', 'Emails'])  # writing data to the file
                df.to_csv(filename + '.csv',index=False,encoding='utf-8')
        except Exception as error:
            print(f"Error: {error}")
            continue





browser.get(str(link))
print("Chrome Browser Invoked")
time.sleep(10)
Selenium_extractor()
