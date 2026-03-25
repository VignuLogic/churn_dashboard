from flask import Flask, render_template, request, redirect
import mysql.connector
from config import DB_CONFIG
import joblib
import numpy as np
import os

app = Flask(__name__)

ml_data = None
if os.path.exists("model.pkl"):
    ml_data = joblib.load("model.pkl")
    print("Model loaded.")

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total customers
    cursor.execute("SELECT COUNT(*) AS total FROM customers")
    total_customers = cursor.fetchone()["total"]

    # Churned customers
    cursor.execute("SELECT COUNT(*) AS churned FROM customers WHERE churn = 1")
    churned = cursor.fetchone()["churned"]

    churn_rate = 0
    if total_customers > 0:
        churn_rate = round((churned / total_customers) * 100, 2)

    # Search customers
    search = request.args.get("search")

    if search:
        query = "SELECT * FROM customers WHERE name LIKE %s"
        cursor.execute(query, ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM customers")

    customers = cursor.fetchall()


    # Contract type data for bar chart
    
    cursor.execute("""
        SELECT contract_type, COUNT(*) AS total
        FROM customers
        GROUP BY contract_type
        """)

    contract_data = cursor.fetchall()

    contracts = [row["contract_type"] for row in contract_data]
    contract_counts = [row["total"] for row in contract_data]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        customers=customers,
        total=total_customers,
        churned=churned,
        rate=churn_rate,
        contracts=contracts,
        contract_counts=contract_counts
    )
    


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



@app.route("/customer/<int:id>")
def customer_detail(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM customers WHERE id = %s", (id,))
    customer = cursor.fetchone()

    cursor.close()
    conn.close()

    if not customer:
        return "Customer not found", 404

    return render_template("customer_detail.html", customer=customer)


# / *** PREDICT TABLE ***/

@app.route("/predict", methods=["GET", "POST"])
def predict():
    prediction = None
    probability = None

    if request.method == "POST":
        if ml_data is None:
            prediction = "Model not ready. Run train_model.py first."
        else:
            try:
                age     = int(request.form["age"])
                monthly = float(request.form["monthly_charge"])
                contract = request.form["contract_type"]

                model      = ml_data["model"]
                le_contract = ml_data["le_contract"]
                le_gender   = ml_data["le_gender"]
                le_payment  = ml_data["le_payment"]

                contract_encoded = le_contract.transform([contract])[0]
                gender_encoded   = le_gender.transform(["Male"])[0]
                payment_encoded  = le_payment.transform(["Credit Card"])[0]
                tenure           = 12

                features = np.array([[age, monthly, contract_encoded,
                                      gender_encoded, tenure, payment_encoded]])

                pred  = model.predict(features)[0]
                proba = model.predict_proba(features)[0]

                churn_prob = round(proba[1] * 100, 1)
                stay_prob  = round(proba[0] * 100, 1)

                if pred == 1:
                    prediction  = "Likely to Churn"
                    probability = churn_prob
                else:
                    prediction  = "Likely to Stay"
                    probability = stay_prob

            except Exception as e:
                prediction = f"Error: {str(e)}"

    return render_template("predict.html",
                           prediction=prediction,
                           probability=probability)

if __name__ == "__main__":
    app.run(debug=True)

    