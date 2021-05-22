from flask import Flask, jsonify
from app.db_util import db

app = Flask(__name__)

@app.route("/")
def get_query_result():
    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()

        response = jsonify(result)
        response.status_code = 200

        return response
