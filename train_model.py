import mysql.connector
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
df = pd.read_sql("SELECT age, monthly_charge, contract_type, churn FROM customers", conn)
conn.close()

print(f"Total rows loaded: {len(df)}")

le = LabelEncoder()
df["contract_encoded"] = le.fit_transform(df["contract_type"])

X = df[["age", "monthly_charge", "contract_encoded"]]
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LogisticRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {round(acc * 100, 1)}%")

joblib.dump({"model": model, "encoder": le}, "model.pkl")
print("Saved to model.pkl — done!")