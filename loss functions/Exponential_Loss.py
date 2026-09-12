import numpy as np

class ExponentialLossLinearClassifier:
    def __init__(self, learning_rate=0.01, epochs=100):
        self.lr = learning_rate
        self.epochs = epochs
        self.w = None
        self.b = None
        self.loss_history = []
        
    def fit(self, X, y):
        # Ensure labels are explicitly -1 and 1
        y = np.asarray(y, dtype=float)
        n_samples, n_features = X.shape
        
        # Initialize weights and bias to zeros
        self.w = np.zeros(n_features)
        self.b = 0.0
        self.loss_history = []
        
        for epoch in range(self.epochs):
            # 1. Forward Pass: compute margins and raw scores f(x)
            f_x = np.dot(X, self.w) + self.b
            margins = y * f_x
            
            # 2. Compute average exponential loss
            sample_losses = np.exp(-margins)
            avg_loss = np.mean(sample_losses)
            self.loss_history.append(avg_loss)
            
            # 3. Compute gradients dL/df(x)
            dL_df = -y * sample_losses
            
            # 4. Compute gradients w.r.t weights and bias
            dw = np.dot(X.T, dL_df) / n_samples
            db = np.sum(dL_df) / n_samples
            
            # 5. Update parameters (Gradient Descent)
            self.w -= self.lr * dw
            self.b -= self.lr * db
            
    def predict_score(self, X):
        # Returns the raw decision boundary scores f(x)
        return np.dot(X, self.w) + self.b

    def predict(self, X):
        # Classify based on the sign of the score
        return np.sign(self.predict_score(X))

# --- Training on a Toy Dataset ---

# Generate linearly separable data (2 features)
np.random.seed(42)
X = np.random.randn(100, 2)
# Define a true boundary where x1 + x2 > 0 is class 1, else class -1
y = np.where(X[:, 0] + X[:, 1] > 0, 1.0, -1.0)

# Instantiate and train the model
model = ExponentialLossLinearClassifier(learning_rate=0.1, epochs=50)
model.fit(X, y)

# Evaluate final training accuracy
predictions = model.predict(X)
accuracy = np.mean(predictions == y)

print(f"Final Weights: {model.w}")
print(f"Final Bias: {model.b:.4f}")
print(f"Final Training Accuracy: {accuracy * 100:.1f}%")
