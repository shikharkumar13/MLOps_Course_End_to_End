# train_model.py — trains a tiny model and saves it as an artifact.
# Part of the Phase 00 (MLOps Track) Part 6 hands-on exercise.
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib

X, y = make_classification(
    n_samples=300, n_features=15, n_informative=4, n_redundant=2,
    n_classes=2, class_sep=1.2, flip_y=0.10, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Test accuracy: {accuracy:.1%}")

joblib.dump(model, "model.joblib")
print("Model saved to model.joblib")
