import time
import threading

def handle_time_out():
    #si pasan 30 segundos y no se ha terminado de ejecutar el codigo, se lanza una excepcion
    time.sleep(30)
    raise TimeoutError

def main():
    try:
        time_out_thread = threading.Thread(target=handle_time_out)
        time_out_thread.start()
        #resto de mi codigo que puede tardar mas de 30 seg
    except TimeoutError:
        print("el codigo tardo demasiado")
        pass
    print("Se finalizo la operacion")