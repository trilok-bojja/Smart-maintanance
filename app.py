from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="predictivemaintenancedb"
    )
    return connection


@app.route("/")
def home():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            Machine_ID,
            Machine_Name,
            Machine_Type,
            Location,
            Installation_Date,
            Operating_Hours,
            Status
        FROM machine
        ORDER BY Machine_ID
    """)

    machines = cursor.fetchall()

    for machine in machines:

        cursor.execute("""
            SELECT
                Temperature,
                Vibration,
                Pressure
            FROM sensor_data
            WHERE Machine_ID = %s
            ORDER BY Reading_DateTime DESC
            LIMIT 1
        """, (machine["Machine_ID"],))

        sensor = cursor.fetchone()

        if sensor:
            machine["Temperature"] = sensor["Temperature"]
            machine["Vibration"] = sensor["Vibration"]
            machine["Pressure"] = sensor["Pressure"]
        else:
            machine["Temperature"] = "-"
            machine["Vibration"] = "-"
            machine["Pressure"] = "-"

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        machines=machines
    )


if __name__ == "__main__":
    app.run(debug=True)