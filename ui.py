import tkinter as tk
from tkinter import ttk, scrolledtext
import customtkinter as ctk
import requests
import threading

class BookRecommendationUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Book Recommendation Chatbot")
        self.window.geometry("1200x800")
        
        # Configure grid layout
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar = ctk.CTkFrame(self.window, width=260)
        self.sidebar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # App name label
        self.app_name = ctk.CTkLabel(self.sidebar, text="Book Recommendation", font=("Arial", 20, "bold"))
        self.app_name.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.chat_button = ctk.CTkButton(self.sidebar, text="Chat", command=self.show_chat)
        self.chat_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.history_button = ctk.CTkButton(self.sidebar, text="History", command=self.show_history)
        self.history_button.grid(row=2, column=0, padx=20, pady=10)
        
        # Clear history button
        self.clear_history_button = ctk.CTkButton(self.sidebar, text="Clear History", command=self.clear_history)
        self.clear_history_button.grid(row=3, column=0, padx=20, pady=10)

        # Main content frame
        self.main_content = ctk.CTkFrame(self.window)
        self.main_content.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(self.main_content, wrap=tk.WORD, font=("Arial", 12), state=tk.DISABLED)
        self.chat_area.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        # Input frame
        self.input_frame = ctk.CTkFrame(self.main_content)
        self.input_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Message input
        self.message_input = ctk.CTkEntry(self.input_frame, placeholder_text="Message Book Recommendation Chatbot...", font=("Arial", 14))
        self.message_input.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        
        # Send button
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=100, command=self.send_message, font=("Arial", 14))
        self.send_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Bind Enter key to send button
        self.message_input.bind("<Return>", self.send_message)

        # History storage
        self.search_history = []

        # Define bold font for important text
        self.bold_font = ('Arial', 12, 'bold')
        self.regular_font = ('Arial', 12)

    def show_chat(self):
        # Implement chat view logic (already active by default)
        pass
        
    def show_history(self):
        # Display search history
        history_str = "\n".join(self.search_history) if self.search_history else "No history found."
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"History:\n{history_str}\n")
        self.chat_area.config(state=tk.DISABLED)
        
    def clear_history(self):
        # Clear chat history
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.search_history = []
        self.chat_area.config(state=tk.DISABLED)

    def send_message(self, event=None):
        message = self.message_input.get()
        if message:
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"You: {message}\n", "you")  # Bold for 'You'
            self.message_input.delete(0, tk.END)

            # Save to search history
            self.search_history.append(message)

            # Start a background thread for chatbot response
            threading.Thread(target=self.get_response_from_flask, args=(message,)).start()

    def get_response_from_flask(self, query):
        # Send the query to Flask backend
        try:
            response = requests.post("http://127.0.0.1:5000/", data={"query": query})
            response_message = response.text
        except requests.exceptions.RequestException as e:
            response_message = "Sorry, I couldn't get a response from the server."

        # Display the response from the chatbot
        self.chat_area.config(state=tk.NORMAL)
        
        # If there are book recommendations in the response
        if "Here are some book recommendations" in response_message:
            books = response_message.split("\n")
            self.chat_area.insert(tk.END, f"BookBot: Here are some book recommendations:\n", "bookbot")  # Bold for 'BookBot'

            # Apply numbering to each book and bold book title and description
            for idx, book in enumerate(books[1:], start=1):
                book_info = book.split(" by ")
                title = book_info[0].strip()
                author = book_info[1].strip() if len(book_info) > 1 else "Unknown Author"
                description = book_info[2].strip() if len(book_info) > 2 else "No description available"

                self.chat_area.insert(tk.END, f"{idx}. ", "number")
                self.chat_area.insert(tk.END, f"{title} ", "title")
                self.chat_area.insert(tk.END, f"by {author}\n", "author")
                self.chat_area.insert(tk.END, f"Description: ", "bold")
                self.chat_area.insert(tk.END, f"{description}\n", "description")

        else:
            # For normal responses, make 'BookBot' bold and add spacing
            self.chat_area.insert(tk.END, f"BookBot: ", "bookbot")  # Bold for 'BookBot'
            self.chat_area.insert(tk.END, response_message + "\n\n")  # Adding space between responses
        
        # Apply bold tags to "You", "BookBot", "Title", "Author", and "Description"
        self.chat_area.tag_config("you", font=self.bold_font)
        self.chat_area.tag_config("bookbot", font=self.bold_font)
        self.chat_area.tag_config("number", font=self.regular_font)  # Regular font for numbering
        self.chat_area.tag_config("title", font=('Arial', 12, 'bold'))  # Bold for book title
        self.chat_area.tag_config("author", font=('Arial', 12, 'italic'))  # Italic for author
        self.chat_area.tag_config("description", font=('Arial', 12))  # Regular font for description
        self.chat_area.tag_config("bold", font=('Arial', 12, 'bold'))  # Bold for "Description" label

        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = BookRecommendationUI()
    app.run()
