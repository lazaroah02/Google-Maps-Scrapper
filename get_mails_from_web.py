import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def get_domain_from_url(url):
    # Usar la función urlparse para obtener un objeto con los componentes de la URL
    objeto = urlparse(url)
    # Acceder al atributo netloc del objeto para obtener el dominio
    dominio = objeto.netloc
    return str(dominio)

def is_valid_email(email):
    patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(patron, email):
        return True
    else:
        return False

def get_mails_from_web(url):
    # Crear una lista vacía para guardar los emails
    emails = []
    
    #validating the url
    if url.startswith("https://") == False:
        url = f"https://{url}"
    if url.endswith("/") == False:
        url = url + "/"    
        
    try:
        print(f"Getting emails from website: {url}  ...")
        # Obtener el contenido de la página web
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        content = response.content

        # Crear un objeto BeautifulSoup con el contenido y el parser html
        soup = BeautifulSoup(content, "html.parser")
    
        # Buscar los enlaces con el atributo href que: empiecen por /, contengan el dominio del sitio o redirigan a un archivo .html
        tags = soup("a")
        links = []
        for tag in tags:
            link = tag.get("href")
            if str(link).startswith("/") or get_domain_from_url(url) in link or ".html" in link:
                links.append(link)
        
        # Reconstruir las rutas agregando el dominio al principio de cada ruta y guardarlas en una lista
        urls = []
        for link in links:
            if "https://" in link:
                urls.append(link)
            else:
                urls.append(url + str(link))

        # Eliminar las URLs duplicadas de la lista
        urls = list(dict.fromkeys(urls))
        # Recorrer las URLs con un bucle
        for url in urls:
            try:
                # Obtener el contenido de cada URL
                response = requests.get(url, headers=headers)
                content = response.content

                # Crear un objeto BeautifulSoup con el contenido y el parser html
                soup = BeautifulSoup(content, "html.parser")

                # Buscar los enlaces con el atributo href que empiecen por mailto
                links = soup.find_all("a", href=re.compile("^mailto"))
                # Extraer los emails de los enlaces y guardarlos en la lista
                for link in links:
                    email = link["href"].replace("mailto:", "")
                    emails.append(email)

                # Buscar los textos que tengan el formato de un email y guardarlos en la lista
                email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                # Buscamos un máximo de 10 resultados
                elements = soup.find_all(["span", "div", "a"], text=re.compile(email_pattern), limit=5) 
                for element in elements:
                    emails.append(element.text)
                    
            except Exception as error1:
                print(f"Error al obtener los emails: {error1}")
                continue        
    except Exception as error2:
        print(f"Error al obtener las rutas de la web: {error2}")
        pass
    
    # Eliminar los emails duplicados de la lista
    emails = list(dict.fromkeys(emails))
    
    return emails

#url = "rred-duct.com"   
#print(get_mails_from_web(url)) 