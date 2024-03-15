import re

def normalize_email(email):
    '''delete the blank spaces, the simbols and others from the email'''
    if(email != ""):
        email = email.replace(" ", "").replace("'", "")
        if "?" in email:
            email = email.split("?")[0] 
    return email  

def verify_email(email):
    '''verify that a email has the correct structure'''
    # Expresión regular para validar un correo electrónico
    patron_email = re.compile(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', re.IGNORECASE)
    # Retorna True si el email coincide con el patrón, de lo contrario False
    return patron_email.match(email) is not None

def centrar_ventana(ancho,alto,raiz):
    x_ventana = raiz.winfo_screenwidth() // 2 - ancho // 2
    y_ventana = raiz.winfo_screenheight() // 2 - alto // 2

    posicion = str(ancho) + "x" + str(alto) + "+" + str(x_ventana) + "+" + str(y_ventana)
    return posicion
