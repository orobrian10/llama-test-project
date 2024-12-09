from flask import Flask, request, render_template
from utils.custom_preprocessing import chat

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/api/gpt2-chatbot", methods=["POST"])
def gpt2_chatbot():
    
    input_message = request.json["message"]
    print("Received message:", input_message)

    response = chat(input_message, "Qwen/Qwen2.5-1.5B")
    response = response.get("response", "")
    print("Generated response:", response)

    return response

@app.route("/api/dialo-chatbot", methods=["POST"])
def dialo_chatbot():
    input_message = request.json["message"]
    print("Received message:", input_message)
    
    response = chat(input_message, "microsoft/DialoGPT-medium")
    response = response.get("response", "")
    print("Generated response:", response)

    return response

if __name__ == "__main__":
    app.run(port=5000)