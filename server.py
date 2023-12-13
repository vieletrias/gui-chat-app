import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, Button

# Setup of GUI formatting 
class ServerGUI:
    def __init__(self, master):
        #Chat window
        self.master = master
        self.master.title("Server Chat Window")

        #Adding scrolling for chat history
        self.chat_history = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.chat_history.pack(expand=True, fill='both')

        #Messages entry
        self.message_entry = Entry(master)
        self.message_entry.pack(expand=True, fill='x')

        #Adds send button for GUI; calls the command to send message when button is pressed 
        self.send_button = Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

        #Adds socket for the server 
        self.server_socket = socket.socket()

        #lists the clients
        self.clients = []

        #calls to setup the server
        self.setup_server()

        #makes thread for receiving messages to show in the chat
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def setup_server(self):
        #Gets host name and ip
        host_name = socket.gethostname()
        ip = socket.gethostbyname(host_name)
        #binds the server socket to a port and prints the name of the host and the ip address to use 
        port = 1234
        self.server_socket.bind((host_name, port))
        print(host_name, '({})'.format(ip))
        # self.name = "Referee"

        #socket will listen for incoming connections 
        self.server_socket.listen()
        print('Waiting for incoming connections...\n')

    #gets the message and broadcasts it to all connected clients
    def send_message(self):
        message = self.message_entry.get()
        self.chat_history.configure(state="normal")
        self.broadcast("Server: {}".format(message))
        self.chat_history.configure(state="disabled")
        self.message_entry.delete(0, tk.END)

    #loops to continue to receive messages 
    def receive_messages(self):
        while True:
            #If connection extablished, accepts incoming connection and prints the ip address and other info 
            client_socket, addr = self.server_socket.accept()
            print("Received connection from ", addr[0], "(", addr[1], ")")
            print('Connection Established. Connected From: {}, ({})'.format(addr[0], addr[0]))

            # Receive client name
            client_name = client_socket.recv(1024).decode()

            #adds name to list of clients
            self.clients.append((client_socket, client_name))
            #broadcasts that a user has joined the chat 
            self.broadcast("{} has joined the chat".format(client_name))

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_name))
            client_handler.start()

    def handle_client(self, client_socket, client_name):
        try:
            while True:
                #receives messages in a loop so that it continues to receive data 
                message = client_socket.recv(1024).decode()
                if not message:
                    break  # Handle disconnection when an empty message is received
                #formats the messages so that the client name and the message sent is being broadcasted 
                self.broadcast("{}: {}".format(client_name, message))

        #error handling for when connection is aborted/closed
        except (ConnectionResetError, ConnectionAbortedError):
            #informs chat that user has been disconnected
            print("Connection with {} was closed".format(client_name))
        finally:
            
            client_socket.close()  # Closes the client socket
            self.remove_client(client_name) #removes client 
            self.broadcast("{} has left the chat".format(client_name)) #broadcast to chat that the user has left 

    #broadcast part where message is being sent
    def broadcast(self, message):
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, message + '\n')
        self.chat_history.configure(state="disabled")
        #loops through each client to send message
        for client, c in self.clients:
            try:
                client.send(message.encode())
            except ConnectionError:
                print("Error sending message to a client")

    #removes client 
    def remove_client(self, client_name):
        for c in self.clients:
            if c[1] == client_name:
                self.clients.remove(c)
                break
    
    #calls for server close 
    def close_server_window(self):
        # Close the server's GUI window
        self.master.destroy()

def main():
    root = tk.Tk()
    ServerGUI(root)
    root.mainloop()

main()
