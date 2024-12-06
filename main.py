import tkinter as tk
import tkinter.messagebox
import webbrowser
import requests
import pywhatkit
import time
import threading
import keyboard

planilha = "" #API LINK
planilha_google = "" #Link para abrir a planilha no google sheets
planilha_sheety = "" #Link para abrir a planilha no sheety no navegador
planilha_individual = '' #Resposta Json
global_name = '' #Salva o nome do funcionário na variavel para ser usado para o método put

stop_task = False


# Criação da janela principal
window = tk.Tk()
window.title("Script de Mensagens")
window.geometry("400x100")

#Função para enviar as mensagens
def send_msg():
    global planilha_individual
    for item in planilha_individual: #Loop para ver os dados na planilha
        if item["enviado"] == "nao" and stop_task == False: #Condição: Mensagem ainda não foi enviada e stop_task é falso
            item["numero"] = f"+{item['numero']}" #Adiciona "+" no começo do número
            msg = f"{item['nome']}, você está sendo convocado para comparecer no posto de saúde Manoel José Ferreira na data {item['data']}.\nCaso não tiver disponibilidade nessa data, entre em contato presencialmente com o posto o mais rápido possível.\nEsta mensagem é automática, não há necessidade de responde-la"
            try:
                pywhatkit.sendwhatmsg_instantly(item["numero"], msg, 10, True) #Envia a mensagem
                print(item["id"])
                celula = f"{planilha}{global_name}/{item['id']}"
                data = {
                    global_name : {
                        "enviado" : "sim"
                    }
                 }
                requests.put(celula, json=data)
            except:
                tkinter.messagebox.showinfo("Error", f"Não foi possível mandar mensagem para {item['name']}. Verifique se o número está no formato correto")
    planilha_individual = ''

#Função para parar o envio de mensagens
def monitor_keyboard():
    global stop_task #Pega a global stop_task
    global planilha_individual
    keyboard.wait('esc') #Escuta a tecla esc
    stop_task = True #Muda a variavel stop_task para True, encerrando o envio de mensagens
    tkinter.messagebox.showinfo("Código interrompido", "O código foi interrompido")
    planilha_individual = ''


#Inicia a sequencia de threads de enviar mensagem e esperar o aperto do botão "esc"
def listen_send():
    global stop_task
    if sheety_entry.get() == '':
        tkinter.messagebox.showinfo("Error", "Por favor, insira um nome válido")
    else:
        resposta = tkinter.messagebox.askyesno("Confirmar", f"Você tem certeza de que quer enviar as mensagens de {name_entry.get()}?")
    stop_task = False #Retorna com stop_task para false
    if resposta:
        nome = name_entry.get() #Salva na variável "nome" o nome que está na entry "name"
        global global_name
        global_name = nome
        sheet = sheety_entry.get() #salva o texto na entry "sheety" na variável "sheet"
        response = requests.get(sheet)
        global planilha_individual
        planilha_individual = response.json()[nome] # Salva a planilha individual da pessoa na global "planilha individual"
        msg_thread = threading.Thread(target=send_msg) # Inicia um thread para mandar mensagem
        monitor_thread = threading.Thread(target=monitor_keyboard, daemon=True) #Inicia outro thread para escutar o pressionar da tecla esc

        msg_thread.start() #inicia a thread de mandar mensagem
        monitor_thread.start() #inicia a thread de escutar a tecla "esc"

        msg_thread.join()

#Função para abrir a planilha no google sheets e no sheety
def abrir():
    webbrowser.open(planilha_sheety)
    webbrowser.open(planilha_google)


#Função para buscar o link do api da planilha do profissional
def buscar():
    sheety_entry.delete(0, tk.END)
    sheet = f"{planilha}{name_entry.get()}"
    response = requests.get(sheet)
    if response.status_code == 404:
        tkinter.messagebox.showinfo("Error", "Esse usuário não existe, certifique-se de essa página está na planilha")
    elif response.status_code == 200:
        sheety_entry.delete(0, tk.END)
        sheety_entry.insert(0, sheet)
        tkinter.messagebox.showinfo("Sucesso!", "Usuário encontrado!")

    elif response.status_code == 402:
        tkinter.messagebox.showinfo("Error!", "Você utilizou a capacidade máxima mensal desse aplicativo")

    else:
        tkinter.messagebox.showinfo("Error", "Certifique-se de que a página da planilha está no formato obrigatório")


# Botões
enviar_btn = tk.Button(window, text="Enviar mensagens", command=listen_send)
enviar_btn.grid(column=1, row =3)

buscar_btn = tk.Button(window, text="Buscar", command=buscar)
buscar_btn.grid(column= 2, row =0)

abrir_btn = tk.Button(window, text="⚙️", command=abrir)
abrir_btn.grid(column= 3, row=0)


#Entry
sheety_entry = tk.Entry(window)
sheety_entry.grid(column = 1, row=1, columnspan=3, sticky="nsew")

name_entry = tk.Entry(window)
name_entry.grid(column = 1, row=0)

# Adicionar um rótulo (label) com texto
nome_funcionario = tk.Label(window, text="Nome do funcionário:")
nome_funcionario.grid(column = 0, row= 0)

link_planilha = tk.Label(window, text="Link da planilha:")
link_planilha.grid(column = 0, row = 1)


# Iniciar o loop principal
window.mainloop()
