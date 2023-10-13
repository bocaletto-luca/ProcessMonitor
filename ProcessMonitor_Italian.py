# Nome Software: Process Monitor
# Author: Bocaletto Luca
# License: GPLv3
# Importa le librerie necessarie
import tkinter as tk  # Per la GUI
from tkinter import ttk
import psutil  # Per ottenere informazioni sui processi
import subprocess  # Per avviare nuovi processi

# Dichiarazione delle variabili globali
colonna_ordinamento = 'name'  # La colonna iniziale per l'ordinamento
ordine_crescente = True  # Ordine iniziale ascendente
colonne_da_mostrare = ["PID", "Nome", "CPU", "Memoria", "Stato", "Utente", "Avvio", "Priorità", "PID Genitore", "Cartella di Lavoro", "Uso Memoria"]
colonne_selezionate = {}  # Dizionario per tenere traccia delle colonne selezionate

# Funzione per mostrare i processi
def mostra_processi(filtro=""):
    # Ottieni una lista di oggetti processo con attributi specifici
    processi = list(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'username', 'create_time', 'nice', 'ppid', 'cwd', 'memory_percent']))

    # Rimuovi i processi dalla visualizzazione
    for row in elenco_processi.get_children():
        elenco_processi.delete(row)

    # Funzione per ottenere il valore di una colonna per un processo
    def get_valore(processo, colonna):
        valore = processo.info.get(colonna)
        return valore if valore is not None else ""

    # Funzione per ottenere il valore 'nice' come intero
    def get_nice_as_int(processo):
        nice = processo.info.get('nice')
        return int(nice) if nice is not None else 0

    # Ordina i processi in base alla colonna di ordinamento e all'ordine
    processi_ordinati = sorted(processi, key=lambda p: get_nice_as_int(p) if colonna_ordinamento == 'nice' else get_valore(p, colonna_ordinamento))
    if not ordine_crescente:
        processi_ordinati.reverse()

    # Aggiungi i processi alla lista
    for processo in processi_ordinati:
        pid = processo.info['pid']
        nome = processo.info['name']
        cpu_percent = processo.info['cpu_percent']
        memoria = processo.info['memory_info'].rss / (1024 * 1024)  # Converti in MB
        status = processo.info['status']
        username = get_valore(processo, 'username')
        create_time = processo.info['create_time']
        nice = processo.info['nice']
        ppid = processo.info['ppid']
        cwd = get_valore(processo, 'cwd')
        memory_percent = processo.info['memory_percent']

        # Filtra i processi in base al filtro inserito e aggiungili alla visualizzazione
        if filtro.lower() in nome.lower():
            elenco_processi.insert('', 'end', values=(pid, nome, f"{cpu_percent:.2f}%", f"{memoria:.2f} MB", status, username, create_time, nice, ppid, cwd, f"{memory_percent:.2f}%"))

# Funzione per cambiare l'ordinamento della colonna
def cambia_ordinamento(colonna):
    global ordine_crescente, colonna_ordinamento
    if colonna == colonna_ordinamento:
        ordine_crescente = not ordine_crescente
    else:
        colonna_ordinamento = colonna
        ordine_crescente = True
    mostra_processi(campo_ricerca.get())

# Funzione per terminare un processo
def termina_processo():
    selezionato = elenco_processi.selection()
    if selezionato:
        pid = int(elenco_processi.item(selezionato, 'values')[0])
        try:
            # Ottieni l'oggetto processo e termina il processo
            processo_da_terminare = psutil.Process(pid)
            processo_da_terminare.terminate()
            mostra_processi()  # Aggiorna la visualizzazione
        except psutil.NoSuchProcess:
            pass

# Funzione per avviare un nuovo processo
def avvia_processo():
    processo_da_avviare = campo_avvia.get()
    try:
        # Avvia il nuovo processo
        subprocess.Popen(processo_da_avviare, shell=True)
        campo_avvia.delete(0, tk.END)  # Cancella il campo di avvio
    except Exception as e:
        tk.messagebox.showerror("Errore", f"Impossibile avviare il processo:\n{str(e)}")  # Mostra un messaggio di errore

# Funzione per mostrare le colonne selezionate
def mostra_colonne_selezionate():
    global colonne_da_mostrare
    colonne_da_mostrare = [col for col, var in colonne_selezionate.items() if var.get() == 1]
    elenco_processi.config(columns=colonne_da_mostrare)  # Configura le colonne visualizzate

    for col in colonne_da_mostrare:
        elenco_processi.heading(col, text=col)
    
    mostra_processi(campo_ricerca.get())  # Aggiorna la visualizzazione

# Funzione per aprire la finestra delle opzioni
def apri_finestra_opzioni():
    finestra_opzioni = tk.Toplevel(root)
    finestra_opzioni.title("Opzioni")

    colonne_frame = tk.Frame(finestra_opzioni)
    colonne_frame.grid(row=0, column=0, rowspan=4, pady=5, padx=10)
    tk.Label(colonne_frame, text="Colonne da mostrare:").grid(row=0, column=0, columnspan=2)

    for i, col in enumerate(colonne_da_mostrare):
        var = tk.IntVar()
        if col in colonne_da_mostrare:
            var.set(1)
        colonne_selezionate[col] = var
        tk.Checkbutton(colonne_frame, text=col, variable=var).grid(row=i + 1, column=0, columnspan=2, sticky="w")

    conferma_colonne_button = tk.Button(colonne_frame, text="Conferma", command=mostra_colonne_selezionate)
    conferma_colonne_button.grid(row=i + 2, column=0, columnspan=2)

# Crea la finestra principale
root = tk.Tk()
root.title("Monitor Process")  # Imposta il titolo

titolo_label = tk.Label(root, text="Monitor Process")
titolo_label.grid(row=0, column=0, columnspan=5, sticky="w")  # Aggiungi un titolo

campo_ricerca = tk.Entry(root, width=20)
campo_ricerca.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="we")  # Campo di ricerca

elenco_processi = ttk.Treeview(root, columns=colonne_da_mostrare, show="headings")
elenco_processi.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky="news")  # Visualizzazione dei processi

scrollbar = ttk.Scrollbar(root, orient="vertical", command=elenco_processi.yview)
scrollbar.grid(row=2, column=5, sticky="ns")
elenco_processi.configure(yscrollcommand=scrollbar.set)  # Barra di scorrimento verticale

scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=elenco_processi.xview)
scrollbar_x.grid(row=3, column=0, columnspan=5, sticky="ew")
elenco_processi.configure(xscrollcommand=scrollbar_x.set)  # Barra di scorrimento orizzontale

for col in colonne_da_mostrare:
    elenco_processi.heading(col, text=col, command=lambda c=col: cambia_ordinamento(c))
    elenco_processi.column(col, width=50, minwidth=50, anchor="center")  # Intestazioni e larghezza delle colonne

avvia_frame = tk.Frame(root)
avvia_frame.grid(row=4, column=0, columnspan=5, pady=10, sticky="w")  # Frame per le azioni

campo_avvia = tk.Entry(avvia_frame, width=20)
campo_avvia.grid(row=0, column=0, padx=5, sticky="w")  # Campo per avviare nuovi processi

avvia_button = tk.Button(avvia_frame, text="Avvia", command=avvia_processo)
avvia_button.grid(row=0, column=1, padx=5, sticky="w")  # Bottone per avviare un nuovo processo

termina_button = tk.Button(avvia_frame, text="Termina Processo", command=termina_processo)
termina_button.grid(row=0, column=2, padx=5, sticky="w")  # Bottone per terminare un processo

aggiorna_button = tk.Button(avvia_frame, text="Aggiorna", command=lambda: mostra_processi(campo_ricerca.get()))
aggiorna_button.grid(row=0, column=3, padx=5, sticky="w")  # Bottone per aggiornare la visualizzazione dei processi

opzioni_button = tk.Button(avvia_frame, text="Opzioni", command=apri_finestra_opzioni)
opzioni_button.grid(row=0, column=4, padx=5, sticky="w")  # Bottone per aprire la finestra delle opzioni

root.grid_rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)

mostra_processi()  # Mostra i processi all'avvio

root.mainloop()  # Avvia l'applicazione
