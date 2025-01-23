# backend/app.py
from flask import Flask
from routes import register_routes  # Absolute import

app = Flask(__name__)
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
