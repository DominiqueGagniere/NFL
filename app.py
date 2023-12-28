from flask import Flask, request
 
app = Flask(__name__)

@app.route("/ip", methodes={'POST'})
def ip():
    data = request.get_json()
    return data

# Flask run pour démarrer