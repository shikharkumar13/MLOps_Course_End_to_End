# predict.py — loads the saved model artifact and makes a prediction.
# This is the script that gets containerized in the Dockerfile.
import joblib
import numpy as np

model = joblib.load("model.joblib")

sample = np.array([[0.5, -1.2, 0.3, 1.1, -0.4, 0.8, -0.6, 0.2,
                     1.4, -0.9, 0.1, -0.3, 0.7, -1.0, 0.4]])

prediction = model.predict(sample)
probability = model.predict_proba(sample)

print(f"Prediction: class {prediction[0]}")
print(f"Confidence: {probability[0][prediction[0]]:.1%}")
