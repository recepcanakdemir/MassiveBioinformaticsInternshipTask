#import psycopg2
#from flask import Flask, render_template,jsonify
#from config import Config

#app = Flask(__name__)

#hostname = 'localhost'
#db = 'TEST'
#username = 'postgres'
#pwd = 'bcdyziKLMA74.'
#port_id = 5432

#def connect_to_database():
    #conn = psycopg2.connect(
        #database = db,
        #user = username,
        #password = pwd,
        #host = hostname,
        #port = port_id
    #)
    #return conn

#@app.route('/')
#def index():
    #conn = connect_to_database()
    #cur = conn.cursor()

    ### Example query
    #cur.execute('SELECT * FROM report_output')
    #data = cur.fetchall()

    #cur.close()
    #conn.close()
    #return jsonify(data) 

#if __name__ == '__main__':
    #app.run(debug=True)


# ------------- SECOND PART --------------------

#from flask import Flask, request, jsonify
#import psycopg2
#from config import Config

#app = Flask(__name__)

#hostname = 'localhost'
#db = 'TEST'
#username = 'postgres'
#pwd = 'bcdyziKLMA74.'
#port_id = 5432

#def connect_to_database():
    #conn = psycopg2.connect(
        #database=db,
        #user=username,
        #password=pwd,
        #host=hostname,
        #port=port_id
    #)
    #return conn

#@app.route('/query', methods=['GET'])
#def query():
    ## Get query parameters
    #page = int(request.args.get('page', 1))
    #page_size = int(request.args.get('page_size', 10))

    ## Calculate offset
    #offset = (page - 1) * page_size

    ## Connect to the database
    #conn = connect_to_database()
    #cur = conn.cursor()

    ## Execute the query
    #cur.execute(f"SELECT * FROM report_output LIMIT %s OFFSET %s", (page_size, offset))

    ## Fetch results
    #data = cur.fetchall()

    ## Close cursor and connection
    #cur.close()
    #conn.close()

    ### Prepare JSON response
    ##response = {
        ##"page": page,
        ##"page_size": page_size,
        ##"count": len(data),
        ##"results": [dict(row) for row in data]
    ##}

    #return jsonify(data)

#@app.route('/')
#def index():
    #conn = connect_to_database()
    #cur = conn.cursor()

    ### Example query
    #cur.execute('SELECT * FROM report_output')
    #data = cur.fetchall()

    #cur.close()
    #conn.close()
    #return jsonify(data) 

#if __name__ == '__main__':
    #app.run(debug=True)

# ------------- THIRD PART --------------------

from flask import Flask, request, jsonify
import psycopg2
from config import Config

app = Flask(__name__)

hostname = 'localhost'
db = 'TEST'
username = 'postgres'
pwd = 'bcdyziKLMA74.'
port_id = 5432

def connect_to_database():
    conn = psycopg2.connect(
        database=db,
        user=username,
        password=pwd,
        host=hostname,
        port=port_id
    )
    return conn
@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'GET':
        # Handle GET request for pagination without filters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        offset = (page - 1) * page_size

        conn = connect_to_database()
        cur = conn.cursor()

        cur.execute("SELECT * FROM report_output LIMIT %s OFFSET %s", (page_size, offset))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)
    elif request.method == 'POST':
        # Handle POST request with filters, ordering, and pagination
        request_data = request.json
        filters = request_data.get('filters', {})
        ordering = request_data.get('ordering', {})
        page = int(request_data.get('page', 1))
        page_size = int(request_data.get('page_size', 10))
        offset = (page - 1) * page_size

        query = "SELECT * FROM report_output WHERE TRUE"
        query_params = []

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

        if ordering:
            order_criteria = []
            for order in ordering:
                column, direction = list(order.items())[0]
                order_criteria.append(f"{column} {direction}")

            query += f" ORDER BY {' , '.join(order_criteria)}"

        # Add pagination to the query
        query += " LIMIT %s OFFSET %s"
        query_params.extend([page_size, offset])

        conn = connect_to_database()
        cur = conn.cursor()

        cur.execute(query, query_params)
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
