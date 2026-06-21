# mlops_phase00_part5_train_and_overfit.py
#
# Hands-on demonstration of train/test splits and overfitting, using a
# synthetic scikit-learn dataset tuned to make the effect clearly visible.
# See Phase 00 (MLOps Track) Part 5, Section 12, for the full explanation.
#
# Setup:
#   pip install scikit-learn
# Run:
#   python mlops_phase00_part5_train_and_overfit.py     (Windows)
#   python3 mlops_phase00_part5_train_and_overfit.py    (Mac)

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# A synthetic classification dataset, tuned to have a real, learnable
# pattern PLUS enough noise that an overly complex model can memorize
# spurious detail instead of the true pattern — this is what makes the
# overfitting demonstration below actually visible (a perfectly clean
# dataset like Iris is too easy for this to show up).
X, y = make_classification(
    n_samples=300,
    n_features=15,
    n_informative=4,
    n_redundant=2,
    n_classes=2,
    class_sep=1.2,
    flip_y=0.10,        # 10% randomly mislabeled — real-world-style noise
    random_state=42,
)

# Split into training data and test data (Section 5 of the guide).
# random_state=42 just makes the split reproducible every time you run this.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

print(f"Training examples: {len(X_train)}")
print(f"Test examples:     {len(X_test)}")


def train_and_evaluate(max_depth, label):
    """
    Train a decision tree and report both training and test accuracy.
    max_depth controls how complex the tree is allowed to become —
    None means "no limit," which is exactly how we'll demonstrate
    overfitting below.
    """
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)   # this is "training" — the model learns

    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)

    train_accuracy = accuracy_score(y_train, train_predictions)
    test_accuracy = accuracy_score(y_test, test_predictions)

    gap = train_accuracy - test_accuracy

    print(f"\n{label}")
    print(f"  Training accuracy: {train_accuracy:.1%}")
    print(f"  Test accuracy:     {test_accuracy:.1%}")
    print(f"  Gap:               {gap:.1%}  "
          f"{'<- overfitting!' if gap > 0.08 else '<- good generalization'}")


if __name__ == "__main__":
    print("=" * 50)
    print("Comparing model complexity")
    print("=" * 50)

    train_and_evaluate(max_depth=3,    label="Simple model (max_depth=3)")
    train_and_evaluate(max_depth=None, label="Unrestricted model (max_depth=None)")

    print("\n" + "=" * 50)
    print("Try changing max_depth above (try 3, 5, 10) and re-running —")
    print("watch how the train/test gap changes as model complexity changes.")
    print("=" * 50)
