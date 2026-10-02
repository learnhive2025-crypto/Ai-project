import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib

data = pd.read_excel(
    "career_ml_dataset.xlsx"
)
print("Dataset:")
print(data)
features = [

    "CS",
    "ENG",
    "BIO",
    "BT",
    "COM",
    "ART",
    "MED",
    "DES"

]
X = data[features]
y = data["Career"]

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42,

    stratify=y

)

model = DecisionTreeClassifier(

    max_depth=5,

    random_state=42

)


model.fit(

    X_train,

    y_train

)


y_pred = model.predict(

    X_test

)


accuracy = accuracy_score(

    y_test,

    y_pred

)


print()
print("Model Accuracy:", accuracy)



joblib.dump(

    model,

    "career_model.pkl"

)


print()
print("career_model.pkl created successfully!")