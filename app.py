import os
from flask import Flask, render_template, request
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except:
    psycopg2 = None

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_conn():
    if DATABASE_URL and psycopg2:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor), "postgres"
    else:
        conn = sqlite3.connect('cyber.db')
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

def init_db():
    conn, db_type = get_conn()
    cur = conn.cursor()
    if db_type == "postgres":
        cur.execute('''CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, name TEXT, phone TEXT, service TEXT, details TEXT, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, service TEXT, details TEXT, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn, db_type = get_conn()
    return render_template('index.html', db_type=db_type.upper())

@app.route('/order', methods=['GET','POST'])
def order():
    if request.method == 'POST':
        name = request.form.get('name'); phone = request.form.get('phone')
        service = request.form.get('service'); details = request.form.get('details')
        conn, db_type = get_conn()
        cur = conn.cursor()
        if db_type == "postgres":
            cur.execute("INSERT INTO orders (name, phone, service, details) VALUES (%s,%s,%s,%s)", (name, phone, service, details))
        else:
            cur.execute("INSERT INTO orders (name, phone, service, details) VALUES (?,?,?,?)", (name, phone, service, details))
        conn.commit(); conn.close()
        return render_template('success.html', name=name)
    return render_template('order.html', selected_service=request.args.get('service',''))

if __name__ == '__main__':
    app.run(debug=True)