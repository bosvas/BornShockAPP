from flask import Flask, render_template, redirect, request
import os
import psycopg2
from dotenv import load_dotenv
import earthquake_api
import chart_generator
from classes.person import Person
from classes.quake import Quake

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
);

CREATE TABLE IF NOT EXISTS quakes(
                        id SERIAL PRIMARY KEY,
                        place VARCHAR(250) NOT NULL,
                        mag FLOAT NOT NULL,
                        date VARCHAR NOT NULL,
                        person_id INT NOT NULL REFERENCES people(id)
);
"""
INSERT_PERSON = """INSERT INTO people (name, date_of_birth, address)
                                VALUES (%s, %s, %s);"""
GET_ONE_BY_ID = "SELECT * FROM people WHERE id = %s"
SELECT_ALL_PEOPLE = "SELECT * FROM people"
SELECT_ALL_QUAKES = "SELECT * FROM quakes"
UPDATE_ONE = "UPDATE people SET name = %s, date_of_birth = %s, address = %s WHERE id = %s"
DELETE_ONE = "DELETE FROM people WHERE id = %s"
GET_QUAKES_BY_PERSON_ID = "SELECT * FROM quakes WHERE person_id = %s"
INSERT_QUAKE = "INSERT INTO quakes (place, mag, date, person_id) VALUES (%s, %s, %s, %s)"
GET_PERSON_ID = "SELECT id FROM people WHERE name = %s"


@app.route('/')
def index():
    return redirect('/people/show')


@app.route("/people/show", methods=['GET'])
def get_all():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_PEOPLE_TABLE)
            cursor.execute(SELECT_ALL_PEOPLE)
            people_tuples = cursor.fetchall()
            people_objects = [Person(*person) for person in people_tuples]
            # some possible actions with list of Persons
            # for example - return people sorted by name value (don't forget to change
            #people_objects_sorted =sorted(people_objects, key=lambda person: person.name)

    return render_template('person/index.html', people=people_objects)


@app.route("/people/new", methods=['GET', 'POST'])
def create_person():
    if request.method == 'POST':
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        address = request.form['address']
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_PEOPLE_TABLE)
                cursor.execute(INSERT_PERSON, (name, date_of_birth, address))
                cursor.execute(GET_PERSON_ID, (name,))
                result = cursor.fetchone()
                current_id = result[0]
                new_person = Person(current_id, name, date_of_birth, address)
                quakes = earthquake_api.get_quakes(new_person)
                for quake in quakes:
                    cursor.execute(INSERT_QUAKE, (quake[0], quake[1], quake[2], current_id))
                    connection.commit()
        return redirect("/people/show")
    return render_template('person/new.html')


@app.route('/people/show/<id>', methods=['GET', 'POST'])
def get_person(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_ONE_BY_ID, (id,))
            person_data = cursor.fetchall()
            person = Person(person_data[0][0], person_data[0][1], person_data[0][2], person_data[0][3])
            cursor.execute(GET_QUAKES_BY_PERSON_ID, (id,))
            quakes_tuples = cursor.fetchall()
            print(quakes_tuples)
            # quakes_objects = [Quake(*quake) for quake in quakes_tuples]
            plot_url = chart_generator.make_chart(quakes_tuples, person.name)

    return render_template("person/show.html", person=person, quakes=quakes_tuples, plot_url=plot_url)


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
    return render_template('person/update.html')


@app.route('/people/delete/<id>', methods=['POST', 'GET'])
def delete_student(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_ONE, (id,))
            connection.commit()

    return redirect("/people/show")

@app.route("/people/quakes", methods=['GET'])
def get_quakes():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_PEOPLE_TABLE)
            cursor.execute(SELECT_ALL_QUAKES)
            quake_tuples = cursor.fetchall()
            cursor.execute(SELECT_ALL_PEOPLE)
            people_tuples = cursor.fetchall()
            people_objects = [Person(*person) for person in people_tuples]
            quake_objects = []
            for quake in quake_tuples:
                # try:
                this_person = next(person for person in people_objects if person.id == quake[4])
                # except StopIteration:
                #     return None
                new_quake = Quake(quake[0], quake[1], quake[2], quake[3], this_person)
                quake_objects.append(new_quake)

    return render_template('quake/index.html', quakes=quake_objects)



if __name__ == '__main__':
    app.run(debug=True, port=5001)
