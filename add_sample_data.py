import mysql.connector
import random
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

random.seed(42)

contract_types = ["Monthly", "One Year", "Two Year"]
genders = ["Male", "Female"]
payment_methods = ["Credit Card", "Bank Transfer", "Cash"]

customers = []

for i in range(300):
    name = f"Customer_{i+1}"
    age = random.randint(18, 70)
    gender = random.choice(genders)
    tenure = random.randint(1, 72)
    contract = random.choice(contract_types)
    payment = random.choice(payment_methods)

    # Realistic Indian rupee monthly charges
    if contract == "Monthly":
        monthly_charge = round(random.uniform(500, 2000), 2)
        churn = 1 if (monthly_charge > 1400 or age < 30 or tenure < 12) else 0
    elif contract == "One Year":
        monthly_charge = round(random.uniform(400, 1500), 2)
        churn = 1 if (monthly_charge > 1200 or tenure < 6) else 0
    else:
        monthly_charge = round(random.uniform(300, 1200), 2)
        churn = 1 if (monthly_charge > 1000 or tenure < 3) else 0

    # Add some randomness
    if random.random() < 0.1:
        churn = 1 - churn

    customers.append((name, age, monthly_charge, contract, churn,
                      gender, tenure, payment))

cursor.executemany(
    """INSERT INTO customers 
       (name, age, monthly_charge, contract_type, churn, gender, tenure, payment_method) 
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
    customers
)

conn.commit()
print(f"Inserted {len(customers)} customers successfully!")
cursor.close()
conn.close()