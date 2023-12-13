import tkinter as tk
from tkinter import scrolledtext
import socket
import time
import threading

#formatting for gui
class ClientGUI:
    def __init__(self, master, server_host, port, name):
        self.master = master
        self.master.title("Chat Application")
        self.server_host = server_host
        self.port = port
        self.name = name

        self.chat_history = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.chat_history.pack(expand=True, fill='both')

        self.message_entry = tk.Entry(master)
        self.message_entry.pack(expand=True, fill='x')

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

        self.client_socket = socket.socket()
        self.client_socket.connect((self.server_host, self.port))
        self.client_socket.send(name.encode())

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    #fxn call to send message 
    def send_message(self):
        self.chat_history.configure(state="normal")
        message = self.message_entry.get()
        self.chat_history.configure(state="disabled")
        #if user enter bye then the application will close as well
        if message == "[bye]":
            self.client_socket.send(message.encode())
            self.client_socket.close()
            self.master.destroy()  # Close the client GUI window upon leaving
        else:
            #if not [bye] then just send the message
            self.client_socket.send(message.encode())
        self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                #receives messages and insert it into chat history
                message = self.client_socket.recv(1024).decode()
                self.chat_history.configure(state="normal")
                self.chat_history.insert(tk.END, message + '\n')
                self.chat_history.configure(state="disabled")
            # except ConnectionAbortedError:
            #     break
            except ConnectionResetError:
                self.chat_history.configure(state="normal")
                self.chat_history.insert(tk.END, "Server closed in 5 seconds.")
                self.chat_history.configure(state="disabled")
                time.sleep(5)
                self.client_socket.close()
                self.master.destroy()
            except:
                break

#main fxn to ask for server ip add and name 
def main():
    server_host = input('Enter server\'s IP address:')
    name = input('Enter your name: ')
    port = 1234

    root = tk.Tk()
    ClientGUI(root, server_host, port, name)
    root.mainloop()

main()