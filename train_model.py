import mysql.connector
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
df = pd.read_sql("""
    SELECT age, monthly_charge, contract_type, 
           gender, tenure, payment_method, churn 
    FROM customers
    WHERE tenure IS NOT NULL 
    AND gender IS NOT NULL 
    AND payment_method IS NOT NULL
""", conn)
conn.close()

print(f"Total rows loaded: {len(df)}")

# Encode contract_type
le_contract = LabelEncoder()
df["contract_encoded"] = le_contract.fit_transform(df["contract_type"])

# Encode gender
le_gender = LabelEncoder()
df["gender_encoded"] = le_gender.fit_transform(df["gender"])

# Encode payment_method
le_payment = LabelEncoder()
df["payment_encoded"] = le_payment.fit_transform(df["payment_method"])

# Features and target
X = df[["age", "monthly_charge", "contract_encoded",
        "gender_encoded", "tenure", "payment_encoded"]]
y = df["churn"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Accuracy
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {round(acc * 100, 1)}%")

# Save everything needed for prediction
joblib.dump({
    "model": model,
    "le_contract": le_contract,
    "le_gender": le_gender,
    "le_payment": le_payment
}, "model.pkl")

print("Saved to model.pkl — done!")