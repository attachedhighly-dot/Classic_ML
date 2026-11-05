import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# 1. Generate Mock Churn Data
np.random.seed(42)
n_samples = 1000

data = {
    'tenure_months': np.random.randint(1, 72, size=n_samples),
    'monthly_charges': np.random.uniform(20.0, 120.0, size=n_samples),
    'total_charges': np.random.uniform(20.0, 8000.0, size=n_samples),
    # Imbalanced target distribution: ~20% churn rate
    'churn': np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2]) 
}
df = pd.DataFrame(data)

# 2. Separate Features and Target
X = df.drop('churn', axis=1).to_numpy()
y = df['churn'].to_numpy()

# 3. Train-Test Split (Stratified to maintain churn ratio)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. Feature Scaling 
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Train Random Forest (using class_weight to manage imbalance)
model = RandomForestClassifier(class_weight='balanced', random_state=42)
model.fit(X_train_scaled, y_train)

# 6. Evaluate Model
y_pred = model.predict(X_test_scaled)

print("--- Confusion Matrix ---")
print(confusion_matrix(y_test, y_pred))

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))
