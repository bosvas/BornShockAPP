from flask import Flask, render_template, redirect, request
import os
import psycopg2
from dotenv import load_dotenv
import earthquake_api
import chart_generator

load_dotenv()

app = Flask(__name__)
url_db = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url_db)

CREATE_PEOPLE_TABLE = """
CREATE TABLE IF NOT EXISTS people(
                       id SERIAL PRIMARY KEY,
                       name VARCHAR(250) NOT NULL,
                       date_of_birth VARCHAR(20) NOT NULL,
                       address VARCHAR(100) NOT NULL       
);"""

INSERT_PERSON = """INSERT INTO people (name, date_of_birth, address)
                                VALUES (%s, %s, %s);"""

GET_ONE_BY_ID = "SELECT * FROM people WHERE id = %s"

UPDATE_ONE = "UPDATE people SET name = %s, date_of_birth = %s, address = %s WHERE id = %s"

DELETE_ONE = "DELETE FROM people WHERE id = %s"


@app.route('/')
def index():
    return redirect('/people/show')


@app.route("/people/show", methods=['GET'])
def get_all():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM people;')
            people = cursor.fetchall()
    return render_template('index.html', people=people)


@app.route("/people/new", methods=['GET', 'POST'])
def create_person():
    if request.method == 'POST':
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        address = request.form['address']
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_PEOPLE_TABLE)
                ## TODO before release delete line of creating table
                cursor.execute(INSERT_PERSON, (name, date_of_birth, address))
        return redirect("/people/show")
    return render_template('new.html')


@app.route('/people/show/<id>', methods=['GET', 'POST'])
def get_person(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_ONE_BY_ID, (id,))
            data = cursor.fetchall()
            person = data[0]

    quakes = earthquake_api.get_quakes(person[2], person[3])
    plot_url = chart_generator.make_chart(quakes, person[1])

    return render_template("show.html", person=person, quakes=quakes, plot_url=plot_url)


@app.route('/people/update/<id>', methods=['POST', 'GET'])
def update_person(id):
    if request.method == 'POST':
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        address = request.form['address']
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_ONE, (name, date_of_birth, address, id))
                connection.commit()
        return redirect("/people/show")
    return render_template('update.html')


@app.route('/people/delete/<id>', methods=['POST', 'GET'])
def delete_student(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_ONE, (id,))
            connection.commit()

    return redirect("/people/show")


if __name__ == '__main__':
    app.run(debug=True, port=5001)
