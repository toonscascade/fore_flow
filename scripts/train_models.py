import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import torch
import torch.nn as nn


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ml_engine.anomaly_detection.isolation_forest import AnomalyDetector
from ml_engine.temporal_forecasting.model import ThreatForecastLSTM
from ml_engine.world_model.state_representation import STATE_DIM
from ml_engine.world_model.state_transition_model import NetworkStateTransitionModel
from network_engine.feature_extractor import FeatureExtractor


def train_anomaly_model(output_path: Path):
    print("--> Training Isolation Forest Anomaly Detection Model...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    np.random.seed(42)
    n_samples = 1500
    n_features = len(FeatureExtractor.FEATURE_NAMES)

    # Generate baseline normal network flow traffic features
    normal_flows = np.random.normal(loc=0.5, scale=0.15, size=(n_samples, n_features))
    # Add a small proportion of anomalous flows (spikes, high packet/byte counts, unusual ports)
    anomalous_flows = np.random.uniform(low=2.0, high=6.0, size=(60, n_features))
    X = np.vstack([normal_flows, anomalous_flows]).astype(np.float32)

    detector = AnomalyDetector(n_estimators=100, contamination=0.04, random_state=42)
    detector.fit(X)
    detector.metadata = {
        "feature_names": FeatureExtractor.FEATURE_NAMES,
        "n_features": n_features,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "version": "v1.0.0",
    }
    detector.save(output_path, metadata=detector.metadata)
    print(f"    [+] Saved anomaly model to {output_path}")


def train_temporal_model(output_path: Path):
    print("--> Training PyTorch LSTM Temporal Forecasting Model...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(42)
    np.random.seed(42)

    model = ThreatForecastLSTM(
        num_features=1,
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
        max_horizon=24,
    )
    model.train()

    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    criterion = nn.MSELoss()

    # Synthetic training batches: sequence length 48, horizon 24
    for _ in range(40):
        t = np.linspace(0, 10, 48)
        batch_x = []
        batch_y = []
        for _ in range(16):
            phase = np.random.uniform(0, np.pi)
            noise = np.random.normal(0, 0.05, size=48)
            seq = np.clip(0.4 + 0.3 * np.sin(t + phase) + noise, 0.05, 0.95)
            # Future 24 hours continues the wave with slight trend
            t_future = np.linspace(10, 15, 24)
            future = np.clip(0.4 + 0.3 * np.sin(t_future + phase), 0.05, 0.95)
            batch_x.append(seq.reshape(48, 1))
            batch_y.append(future)

        x_tensor = torch.tensor(np.array(batch_x), dtype=torch.float32)
        y_tensor = torch.tensor(np.array(batch_y), dtype=torch.float32)

        optimizer.zero_grad()
        pred = model(x_tensor, horizon=24)
        loss = criterion(pred, y_tensor)
        loss.backward()
        optimizer.step()

    model.eval()
    # Save the full model for torch.load in ForecastService
    torch.save(model, str(output_path))
    print(f"    [+] Saved temporal forecasting model to {output_path}")


def train_world_model(output_path: Path):
    print("--> Training Network State Transition World Model...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    state_dim = STATE_DIM
    model = NetworkStateTransitionModel(
        state_dim=state_dim,
        hidden_size=64,
        num_layers=2,
    )
    model.train()

    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    mse = nn.MSELoss()
    bce = nn.BCELoss()

    for _ in range(25):
        batch_states = torch.rand(16, 12, state_dim)
        target_next = torch.rand(16, 5, state_dim)
        target_risk = torch.rand(16, 5, 1)

        optimizer.zero_grad()
        pred_states, pred_risks = model(batch_states, k_steps=5)
        loss = mse(pred_states, target_next) + bce(pred_risks, target_risk)
        loss.backward()
        optimizer.step()

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "model_config": {
            "state_dim": state_dim,
            "hidden_size": 64,
            "num_layers": 2,
        },
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    torch.save(checkpoint, str(output_path))
    print(f"    [+] Saved world model checkpoint to {output_path}")


def main():
    print("=== Training Forecast AI Engine Models ===")
    anomaly_path = ROOT_DIR / "ml_engine" / "saved_models" / "anomaly_model.pkl"
    temporal_path = ROOT_DIR / "ml_engine" / "saved_models" / "temporal_model.pt"
    world_path = ROOT_DIR / "models" / "network_world_model.pth"

    train_anomaly_model(anomaly_path)
    train_temporal_model(temporal_path)
    train_world_model(world_path)

    print("\nAll AI models successfully generated and saved!")


if __name__ == "__main__":
    main()
