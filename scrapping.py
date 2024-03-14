from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.options import Options
from get_mails_from_web import get_mails_from_web 

options = Options()
options.binary_location = "chrome-win64/chrome.exe"
browser = webdriver.Chrome(options=options)

def Selenium_extractor(callback_log_function, scrapping_successfull, update_state_index, filename = "", file_path = ""):
    try:
        record = []
        e = []
        le = 0 #esta variable contara el # de intentos de obtener resultados para cada pagination scroll que se haga
        results_limit = 1000
        action = ActionChains(browser)
        #lista con los resultados de busqueda, los elementos con la clase "hfpxzc" son los links <a> que llevan al detalle de cada lugar
        a = browser.find_elements(By.CLASS_NAME, "hfpxzc") 

        callback_log_function("Scrolling to capture search results ...")
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
                if le > 3:
                    break
            else:
                le = 0
        
        #close search recommendation
        try:
            # get raiting button
            rating_button = browser.find_elements(By.CLASS_NAME, "uEubGf")[0]

            # Mover el cursor y hacer click
            action.move_to_element(rating_button)
            action.click(rating_button)
            action.perform()
            time.sleep(2)
        except Exception as click_err:   
            callback_log_function(f"Error en el click para cerrar recomendaciones de busqueda: {click_err}") 
              
        callback_log_function("Scrapping info from each search results ...")
        for element in a:
            try:
                #recupero el elemento i de la lista de resultados como un objeto de scroll
                scroll_origin = ScrollOrigin.from_element(element) 
                #hago scroll hasta el elemento 
                action.scroll_from_origin(scroll_origin, 0, 1000).perform()
                #muevo el mouse hasta el centro del elemento
                action.move_to_element(element).perform()
                #hago click en el elemento
                element.click()
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
                    if website != "Not available":
                        mails = tuple(get_mails_from_web(website, callback_log_function=callback_log_function))
                    else:
                        mails = ()      
                    
                    callback_log_function([name, phone, address, website, mails])
                    record.append((name,phone,address,website,mails))
                    df=pd.DataFrame(record,columns=['Name','Phone number','Address','Website', 'Emails'])  # writing data to the file
                    df.to_csv(file_path+filename + '.csv',index=False,encoding='utf-8')
            except Exception as error:
                callback_log_function(f"Error: {error}")
                continue
        scrapping_successfull()    
    except Exception as err:
        callback_log_function(f"Error haciendo scroll: {err}")
        update_state_index()
        pass

def main_scrapping( state, file_path, keywords, callback_log_function, scrapping_successfull, update_state_index, country = "United+States"):    
    filename = state
    link = f"https://www.google.com/maps/search/{keywords}+{state}+{country}"
    browser.get(str(link))
    time.sleep(10)
    Selenium_extractor(
        filename = filename, 
        file_path = file_path, 
        callback_log_function = callback_log_function, 
        scrapping_successfull = scrapping_successfull,
        update_state_index = update_state_index
        )