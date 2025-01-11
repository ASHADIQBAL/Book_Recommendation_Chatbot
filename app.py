from flask import Flask, request
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Chatbot responses for greetings or general queries
def handle_conversation(query):
    chatbot_name = "BookBot"
    greetings = ["hello", "hi", "hey", "greetings"]
    name_queries = ["what is your name", "who are you"]

    if query.lower() in greetings:
        return f"Hi there! I'm {chatbot_name}. How can I help you with book recommendations today?"
    elif query.lower() in name_queries:
        return f"My name is {chatbot_name}, your friendly book recommendation assistant!"
    else:
        return "Sorry, I can only assist with book recommendations. Please try asking about books!"

# Fetch book recommendations from Google Books API
def get_book_recommendations(query):
    api_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'maxResults': 5,
        'key': os.getenv("API_KEY")
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        books = []
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            sale_info = item.get('saleInfo', {})

            book = {
                'title': volume_info.get('title', 'No Title Available'),
                'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                'description': volume_info.get('description', 'No Description Available'),
                'buy_link': sale_info.get('buyLink', 'No Buy Link Available'),
                
            }
            books.append(book)

        return books

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/', methods=['POST'])
def home():
    query = request.form.get('query', '').strip()
    if query:
        conversational_response = handle_conversation(query)
        if conversational_response.startswith("Sorry") or "assist" in conversational_response:
            books = get_book_recommendations(query)
            if books:
                response_message = f"Here are some book recommendations for '{query}':"
                book_list = "\n".join([f"{book['title']} by {book['author']}\nDescription: {book['description']}" for book in books])
                response_message += "\n" + book_list
            else:
                response_message = f"Sorry, I couldn't find any books for '{query}'. Try a different search!"
        else:
            response_message = conversational_response
        return response_message

    return "Sorry, there was an error with your query."

if __name__ == "__main__":
    app.run(debug=True)
