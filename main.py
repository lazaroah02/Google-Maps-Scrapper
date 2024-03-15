import os
import threading
from tkinter import *
from utils import centrar_ventana
from tkinter import messagebox, filedialog
from scrapping import main_scrapping

class Main():
    def __init__(self):
        #variable that follow the reference of the states to delete the scrapped states from the states textarea 
        self.state_index = 1
        
        #creamos la ventana
        self.root = Tk()

        #propiedades de la ventana
        self.root.title("Goole Maps Scrapper") # titulo de la ventana
        self.root.resizable(0,0) # permite modificar el alto y el ancho de la ventana si los valores son 1,1
        self.root.geometry(centrar_ventana(500, 700, self.root)) # posicionamiento de la ventana (ancho X alto + pixeles a la derecha + pixeles hacia abajo)
        
        #logo
        self.absolute_folder_path = os.path.dirname(os.path.realpath(__file__))
        self.icon_path = os.path.join(self.absolute_folder_path, './logo.png')
        self.icon = PhotoImage(file = self.icon_path)
        self.root.iconphoto(True, self.icon)
        
        #frame que contiene los elementos
        self.frame = Frame() # se crea el frame
        self.frame.pack(fill = "both", expand = "true")
        self.frame.config(width = "500", height = "500") 

        #label del input keyword
        self.label_keyword = Label(self.frame, text = "Keyword")
        self.label_keyword.place(x = 10, y = 10 )   
        
        #input para las keywords
        self.input_keyword = Entry(self.frame)
        self.input_keyword.config(width = 50)
        self.input_keyword.place(x = 100, y = 10)
        
        #label carpeta de destino
        self.label_ruta_destino = Label(self.frame, text = "Ruta de destino")
        self.label_ruta_destino.place(x = 10, y = 60 )   
        
        #input para la ruta de la carpeta de destino
        self.input_ruta_destino = Entry(self.frame)
        self.input_ruta_destino.config(width = 50)
        self.input_ruta_destino.place(x = 100, y = 60)
        
        #boton para seleccionar la ruta de la carpeta de destino
        self.button_select_ruta = Button(self.frame, text = "Seleccionar", command = self.seleccionar_ruta_destino)
        self.button_select_ruta.place(x = 420, y = 55)
        
        #label country
        self.label_country = Label(self.frame, text = "Country")
        self.label_country.place(x = 10, y = 110 )   
        
        #input para el country
        self.input_country = Entry(self.frame)
        self.input_country.config(width = 50)
        self.input_country.place(x = 100, y = 110)
        
        #label states
        self.label_states = Label(self.frame, text = "States (Set the states one per line)")
        self.label_states.place(x = 10, y = 145 )   
        
        #button to load United States states 
        self.button = Button(self.frame, text = "Load States", command = self.load_us_states)
        self.button.config()
        self.button.place(x = 200, y = 140)
        
        #textarea states
        self.text_area_states = Text(self.frame)
        self.text_area_states.config(width = 60, height = 10)
        self.text_area_states.place(x = 10, y = 170)
        
        #button para iniciar el scrapping 
        self.button = Button(self.frame, text = "Iniciar Scrapping", command = self.prepare_scrapping)
        self.button.config()
        self.button.place(x = 10, y = 350)
        
        #label to show the loading status
        self.label_loading = Label(self.frame, text = "Realizando Scrapping")
        self.label_loading.config(fg = "blue", font = ("Cabin", 15,), width = 18)
        
        self.x_coordenate_of_loading_points = 330
        self.after_function_id = None
        self.loading_points = Label(self.frame, text = ". . .")
        self.loading_points.config(fg = "blue", font = ("Courier", 15, "italic"))
        
        #show log textarea
        self.text_area_log = Text(self.frame)
        self.text_area_log.config(width = 60, height = 18)
        self.text_area_log.place(x = 8, y = 400)
                
        self.root.mainloop()
        
    def seleccionar_ruta_destino(self):
        self.input_ruta_destino.delete(0, "end")
        path = str(filedialog.askdirectory())
        self.input_ruta_destino.insert(0, path)
        
    def prepare_scrapping(self):
        keyword = self.input_keyword.get().replace(" ", "+")
        ruta_destino = self.input_ruta_destino.get()
        #check if the folder path ends with "/", in case that not, added it
        if ruta_destino.endswith("/") == False:
            ruta_destino += '/'
        country = self.input_country.get().replace(" ", "+")
        states = self.text_area_states.get("1.0", END).split("\n")
        if states[-1] == '':
            states.remove('')

        #check that any field is empty
        if keyword == "" or ruta_destino == "" or country == "" or states == []:
            messagebox.showinfo("!","No pueden haber campos vacios")
        else:
            t = threading.Thread(target = self.start_scrapping, args = [keyword, ruta_destino, states, country])
            t.start()   
              
    def start_scrapping(self, keyword, ruta_destino, states, country):
        self.disable_buttons()
        self.show_loading_status()

        for state in states:
            self.callback_log_function(f"Starting scrapping for: {state} {self.input_country.get()}. Searching for: {self.input_keyword.get()}")
            try:
                main_scrapping(
                    file_path=ruta_destino, 
                    keywords=keyword, 
                    state = state, 
                    callback_log_function=self.callback_log_function, 
                    country = country, 
                    scrapping_successfull = self.remove_state_from_scrapping_list,
                    update_state_index = self.update_state_index
                    )
            except Exception:
                self.callback_log_function(f"Herror en el scrapping for: {state} {self.input_country.get()}. Searching for: {self.input_keyword.get()}") 
                continue  
                
        messagebox.showinfo("!","Operacion finalizada")
        self.hide_loading_status()
        self.enable_buttons()
              
    def enable_buttons(self):
        self.button.config(state = "normal")
        self.button_select_ruta.config(state = "normal")
        
    def disable_buttons(self):
        self.button.config(state = "disabled")
        self.button_select_ruta.config(state = "disabled")
    
    # Define a function to animate the GIF
    def show_loading_status(self, frame = 0):
        if self.loading_points.winfo_x() >= 350:
            self.loading_points.place(x = self.x_coordenate_of_loading_points)
            frame = 0
        # Update the position of the loading point
        self.label_loading.place(x = 130, y = 345)     
        self.loading_points.place(x = (self.x_coordenate_of_loading_points + frame), y = 346)
        # Schedule the next frame to be displayed after 250 milliseconds
        self.after_function_id = self.root.after(250, self.show_loading_status, frame + 5)
    
    def hide_loading_status(self):
        self.root.after_cancel(self.after_function_id)
        self.label_loading.place_forget()    
        self.loading_points.place_forget()   

    def callback_log_function(self, log):
        '''function to show a log in the log textarea'''
        self.text_area_log.insert(END, f"•{log}\n \n")
        self.text_area_log.see("end")

    def remove_state_from_scrapping_list(self):
        '''Remove a state from the textarea states when the scrapping for that state was ok.'''
        self.text_area_states.delete(f'{self.state_index}.0',f'{self.state_index}.end+1c')
    
    def update_state_index(self):
        '''
        Increase the state_index value in 1 when a state scrapping goes bad. 
        This to keep that state in the states textarea in case the user want to re-scrapping the states that fails
        '''
        self.state_index += 1
    
    def load_us_states(self):
        '''Load automatically us states and insert into states textarea'''
        self.text_area_states.delete("1.0", END)  
        try:
            absolute_folder_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(absolute_folder_path, './us_states.txt')
            file = open(file_path, encoding="utf-8")
            states = file.readlines()
            file.close()
            cont = 1
            for state in states:
                self.text_area_states.insert(f"{cont}.0", state)
                cont += 1
        except:
            messagebox.showinfo("!","Error al cargar los estados de Estados Unidos. Ingreselos manualmente")    
        
Main()        