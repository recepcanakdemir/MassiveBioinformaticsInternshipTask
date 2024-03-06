from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import errors
from config import Config

app = Flask(__name__)

# get host properties
hostname = 'localhost'
db = 'databasename'
username = 'username'
pwd = 'password'
port_id = 5432

# database connection
def connect_to_database():
    conn = psycopg2.connect(
        database=db,
        user=username,
        password=pwd,
        host=hostname,
        port=port_id
    )
    return conn

# this query methods takes both get and post methods
@app.route('/assignment/query', methods=['GET', 'POST'])
def query():
    try:
        if request.method == 'GET': # if it is get then pagination will be active
            page = int(request.args.get('page', 1)) # gets page parameter default is 1
            page_size = int(request.args.get('page_size', 10)) # gets page_size default is 10
            offset = (page - 1) * page_size

            conn = connect_to_database()
            cur = conn.cursor()

            cur.execute("SELECT * FROM report_output LIMIT %s OFFSET %s", (page_size, offset))
            data = cur.fetchall()

            cur.close()
            conn.close()

            if not data:
                return jsonify({"message": "No results found."})

            response = {
                "page": page,
                "page_size": page_size,
                "count": len(data),
                "results": [dict(zip([desc[0] for desc in cur.description], row)) for row in data]
            }

            return jsonify(response)

        elif request.method == 'POST': # if it is POST method, then the filter body will be recieved and filtering will be active by this filters body
            request_data = request.json
            filters = request_data.get('filters', {})
            ordering = request_data.get('ordering', [])
            page = int(request_data.get('page', 1))
            page_size = int(request_data.get('page_size', 10))
            offset = (page - 1) * page_size
            query = "SELECT * FROM report_output WHERE TRUE"
            query_params = []

            # Apply filters
            if filters:
                for column, value in filters.items():
                    if value is None:
                        query += f" AND {column} IS NULL"
                    elif isinstance(value, list):
                        query += f" AND {column} IN ({','.join(['%s' for _ in range(len(value))])})"
                        query_params.extend(value)
                    elif isinstance(value, int) or isinstance(value, float):
                        query += f" AND {column} = %s"
                        query_params.append(value)
                    else:
                        query += f" AND {column} ILIKE %s"
                        query_params.append(f"%{value}%")

            # Apply ordering
            if ordering:
                order_criteria = []
                for order in ordering:
                    column, direction = list(order.items())[0]
                    order_criteria.append(f"{column} {direction}")

                query += f" ORDER BY {', '.join(order_criteria)}"

            # Apply pagination
            query += " LIMIT %s OFFSET %s"
            query_params.extend([page_size, offset])

            conn = connect_to_database()
            cur = conn.cursor()

            cur.execute(query, query_params)
            data = cur.fetchall()

            cur.close()
            conn.close()

            if not data:
                return jsonify({"message": "No results found."})

            response = {
                "page": page,
                "page_size": page_size,
                "count": len(data),
                "results": [dict(zip([desc[0] for desc in cur.description], row)) for row in data]
            }

            return jsonify(response)
    # error handling for not finding result and type conflict
    except psycopg2.Error as e:
        if isinstance(e, errors.UndefinedFunction) and '~~*' in str(e):
            return jsonify({"error": "Type conflict: ILIKE operator does not support numeric types."}), 400
        else:
            return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
