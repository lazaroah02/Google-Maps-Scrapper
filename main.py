from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.options import Options
from get_mails_from_web import get_mails_from_web 
import signal

options = Options()
options.binary_location = "chrome-win64/chrome.exe"
browser = webdriver.Chrome(options=options)

def timeout_handler(signum, frame):
    # Esta función se ejecuta cuando se alcanza el tiempo límite
    raise TimeoutError # Lanza el error

def Selenium_extractor():
    record = []
    e = []
    le = 0 #esta variable contara el # de intentos de obtener resultados para cada pagination scroll que se haga
    results_limit = 1000
    action = ActionChains(browser)
    #lista con los resultados de busqueda, los elementos con la clase "hfpxzc" son los links <a> que llevan al detalle de cada lugar
    a = browser.find_elements(By.CLASS_NAME, "hfpxzc") 

    print("Scrolling to capture search results ...")
    #con este bucle se hacen las paginaciones simulando el scroll del usuario 
    while len(a) < results_limit:
        var = len(a)
        #scroll hasta el ultimo resultado de busqueda
        browser.execute_script ('''
                                document.querySelector('[role=\"feed\"]').scrollTo({
                                    top:document.querySelector('[role=\"feed\"]').scrollHeight, 
                                    left:0, 
                                    behavior:'smooth'});
                                ''')
        time.sleep(5)
        #se guarda en la lista "a" todos los resultados de busqueda existentes antes del scroll y despues
        a = browser.find_elements(By.CLASS_NAME, "hfpxzc")

        #numero de intentos de obtener resultados para cada paginacion
        if len(a) == var:
            le+=1
            if le > 5:
                break
        else:
            le = 0
            
    print("Scrapping info from each search results ...")
    for i in range(len(a)-1): #dejo el ultimo resultado de busqueda sin visitar para evitar dar click en el boton "go to top"
        try:
            #recupero el elemento i de la lista de resultados como un objeto de scroll
            scroll_origin = ScrollOrigin.from_element(a[i]) 
            #hago scroll hasta el elemento 
            action.scroll_from_origin(scroll_origin, 0, 1000).perform()
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
                
                #ESTABLESCO UN TIEMPO LIMITE DE 5 MIN PARA BUSCAR LOS MAILS
                # Establece el manejador de señales para el tiempo límite
                signal.signal(signal.SIGALRM, timeout_handler)

                # Establece el tiempo límite en segundos (5 minutos = 300 segundos)
                signal.alarm(300)
                
                try:
                    #busco los mails del sitio web
                    mails = tuple(get_mails_from_web(website))
                except:    
                   print("La extraccion de mails tardo demasiado")
                finally:
                    # Desactiva el tiempo límite
                    signal.alarm(0)   
                   
                print([name, phone, address, website, mails])
                record.append((name,phone,address,website,mails))
                df=pd.DataFrame(record,columns=['Name','Phone number','Address','Website', 'Emails'])  # writing data to the file
                df.to_csv(filepath+filename + '.csv',index=False,encoding='utf-8')
        except Exception as error:
            print(f"Error: {error}")
            continue


us_states = [ "Minnesota", "Misisipi", "Misuri", "Montana", "Nebraska", "Nevada", "Nueva Jersey", 
             "Nueva York", "Nuevo Hampshire", "Nuevo México", "Ohio", "Oklahoma", "Oregón", "Pensilvania", 
             "Rhode Island", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Virginia Occidental", 
             "Washington", "Wisconsin", "Wyoming"]


filepath = "D:/Projects/Mail_Scrapping/data/boats"
keywords = "boat+and+yacht+construction,+repair,+and+assembly+companies+in"

for state in us_states:
    filename = state
    link = f"https://www.google.com/maps/search/{keywords}+{state}+United+States"
    browser.get(str(link))
    print("Chrome Browser Invoked")
    time.sleep(10)
    Selenium_extractor()
