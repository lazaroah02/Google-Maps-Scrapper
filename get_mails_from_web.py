import requests
from bs4 import BeautifulSoup
import re
from numba import njit

files_extensions = [".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".mp4", ".mp3", ".pdf"]
headers = {"User-Agent": "Mozilla/5.0"}

# Definir una función para obtener el dominio de una url
@njit
def get_domain_from_url(url):
    return url.split("//")[-1].split("/")[0]

# Definir una función para validar y normalizar una url
@njit
def normalize_url(url):
    if not url.startswith("https://"):
        url = f"https://{url}"
    if not url.endswith("/"):
        url = url + "/"
    return url

def get_mails_from_route(url):
    emails = []
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
    
    # Eliminar los emails duplicados de la lista
    emails = list(dict.fromkeys(emails))
    return emails    
                    
def rebuild_routes(links, web_url):
    # Reconstruir las rutas agregando el dominio al principio de cada ruta y guardarlas en una lista
    urls = []
    for link in links:
        if "https://" in link:
            urls.append(link)
        else:
            urls.append(web_url + str(link))
    return urls        
                                  
def get_mails_from_web(web_url):
    # Crear una lista vacía para guardar los emails
    emails = []
    no_more_mails_necesary = False
    
    # Validar y normalizar la url
    web_url = normalize_url(web_url)   
        
    try:
        print(f"Getting emails from website: {web_url}  ...")
        # Obtener el contenido de la página web
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(web_url, headers=headers)
        content = response.content

        # Crear un objeto BeautifulSoup con el contenido y el parser html
        soup = BeautifulSoup(content, "html.parser")
    
        # Buscar los enlaces con el atributo href que: empiecen por /, contengan el dominio del sitio o redirigan a un archivo .html
        tags = soup("a")
        links = []
        for tag in tags:
            link = tag.get("href")
            #compruebo si el enlace es para un email
            if "mailto:" in link:
                emails.append(link.split(":")[1])
                no_more_mails_necesary = True
                continue
            #si existe una pagina de contacto voy directamente a esa    
            if "contact" in link:
                emails.extend(get_mails_from_route(rebuild_routes([link], web_url)[0]))
                no_more_mails_necesary = True
                continue
            #si el link contiene algun archivo ej: .mp4 lo saltamos
            if any(ext in link for ext in files_extensions):
                continue  
            else: 
                #compruebo si el enlace es una ruta   
                if str(link).startswith("/") or get_domain_from_url(web_url) in link or ".html" in link:
                    links.append(link)
        
        if no_more_mails_necesary == False: 
            urls = rebuild_routes(links, web_url)
            
            # Eliminar las URLs duplicadas de la lista
            urls = list(dict.fromkeys(urls))
            
            #quedarme con solo las 10 primeras rutas
            if len(urls) > 10:
                urls = urls[0: 10]
            
            #recorro todas las rutas en busca de mails
                for url in urls:
                    try:
                        emails.extend(get_mails_from_route(url)) 
                    except:
                        continue    
    except Exception as e:
        print(f"Error al obtener las rutas de {web_url}: {e}")
        pass
    
    # Eliminar los emails duplicados de la lista
    emails = list(dict.fromkeys(emails))
    
    return emails
