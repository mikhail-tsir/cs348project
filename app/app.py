from flask.json import jsonify
from app.setup import app
from app.db_util import db
from flask import jsonify


@app.route("/")
def get_query_result():
    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()

        response = jsonify(result)
        response.status_code = 200

        return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
