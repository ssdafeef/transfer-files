from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np

# Training data used for demo purposes
X = np.array([
    [1,1,1,1],  # Normal handshake complete
    [3,0,0,0],  # Repeated SYNs, threat
    [2,1,0,0],  # Incomplete handshake, threat
    [1,0,0,0],  # Single SYN no progress, threat
    [1,1,1,1],  # Normal handshake again
    [0,0,0,0],  # No activity, normal
    [4,0,0,0],  # More SYNs, threat
    [1,1,0,1],  # Almost complete handshake
])
y = np.array([0,1,1,1,0,0,1,0])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
mlp = MLPClassifier(hidden_layer_sizes=(8,4), max_iter=500, random_state=42)
mlp.fit(X_scaled, y)

def extract_features(packets):
    state = "START"
    syn_count, syn_ack_count, ack_count, handshake_completed = 0, 0, 0, 0
    for packet in packets:
        p = packet.strip().upper()
        if state == "START":
            if p == "SYN":
                syn_count += 1
                state = "SYN_SEEN"
        elif state == "SYN_SEEN":
            if p == "SYN-ACK":
                syn_ack_count += 1
                state = "SYN_ACK_SEEN"
            elif p == "SYN":
                syn_count += 1
            else:
                state = "START"
        elif state == "SYN_ACK_SEEN":
            if p == "ACK":
                ack_count += 1
                handshake_completed = 1
                state = "START"
            elif p == "SYN":
                syn_count += 1
                state = "SYN_SEEN"
            else:
                state = "START"
    return np.array([syn_count, syn_ack_count, ack_count, handshake_completed])

def explain_features(features):
    syn_count, syn_ack_count, ack_count, handshake_completed = features
    explanation = []
    explanation.append(f"SYN packets seen: {syn_count} (Initiate connections)")
    explanation.append(f"SYN-ACK packets seen: {syn_ack_count} (Server acknowledges SYN)")
    explanation.append(f"ACK packets seen: {ack_count} (Client acknowledges SYN-ACK)")
    explanation.append("Handshake completed" if handshake_completed else "Handshake incomplete")
    return "\n".join(explanation)

def main():
    print("Enter a sequence of packets separated by commas (e.g., SYN, SYN-ACK, ACK):")
    user_input = input()
    packets = user_input.split(',')

    features = extract_features(packets)
    features_scaled = scaler.transform([features])
    pred = mlp.predict(features_scaled)[0]
    prob = mlp.predict_proba(features_scaled)[0][pred]

    print("\n--- Analysis Report ---")
    print(explain_features(features))
    print(f"AI model prediction: {'Threat' if pred == 1 else 'Normal Traffic'} (Confidence: {prob:.2f})")

    if pred == 1:
        print("Final Decision: Threat Detected!")
    else:
        print("Final Decision: Traffic Normal")

if __name__ == "__main__":
    main()
