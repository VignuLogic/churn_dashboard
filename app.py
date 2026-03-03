from flask import Flask, render_template, request, redirect
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    # Total customers
    cursor.execute("SELECT COUNT(*) AS total From customers")
    total_customers = cursor.fetchone()["total"]

    # Churned customers
    cursor.execute("SELECT COUNT(*) AS churned FROM customers WHERE churn = 'yes'")
    churned = cursor.fetchone()["churned"]

    churn_rate = 0
    if total_customers > 0:
        churn_rate = round((churned / total_customers) * 100, 2)

   
   # Fetch all customers
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("dashboard.html", 
                           customers=customers,
                           total=total_customers,
                           churned=churned,
                           rate=churn_rate)


# DELETE BUTTON
@app.route("/delete/<int:id>")
def delete_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM customers WHERE id = %s", (id,))

    conn.commit()   
    cursor.close()
    conn.close()

    return redirect("/")

@app.route("/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        monthly = request.form["monthly_charge"]
        contract = request.form["contract_type"]
        churn = request.form["churned"]

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO customers (name, age, monthly_charge, contract_type, churn)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, age, monthly, contract, churn))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    return render_template("add_customer.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        monthly = request.form["monthly_charge"]
        contract = request.form["contract_type"]
        churn = request.form["churned"]

        cursor.execute("""
        UPDATE customers
        SET name = %s, age = %s, monthly_charge = %s, contract_type = %s, churn = %s
        WHERE id = %s
        """,(name,age,monthly,contract,churn,id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    cursor.execute("SELECT * FROM customers WHERE id = %s", (id,))
    customer = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_customer.html", customer=customer)

if __name__ == "__main__":
    app.run(debug=True)