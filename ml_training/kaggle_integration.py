# ml_training/kaggle_integration.py - FIXED VERSION
import pandas as pd
import numpy as np
import os
from datetime import datetime


class KaggleIntegration:
    def __init__(self):
        self.data_path = "data/kaggle_datasets"
        self.processed_path = "data/processed_datasets"
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.processed_path, exist_ok=True)

    def download_datasets(self):
        """Create dataset structure"""
        print("📥 Setting up dataset structure...")
        try:
            dataset_files = {
                'etc_51_attack.csv': ['timestamp', 'block_height', 'block_time', 'difficulty', 'is_51_attack'],
                'blockchain_anomalies.csv': ['timestamp', 'transaction_volume', 'gas_price', 'anomaly_type'],
            }

            for filename, columns in dataset_files.items():
                empty_df = pd.DataFrame(columns=columns)
                empty_df.to_csv(f"{self.data_path}/{filename}", index=False)

            # Create sample data for demo
            self._create_sample_data()
            print("✅ Dataset structure created with sample data!")
            return True
        except Exception as e:
            print(f"❌ Dataset setup failed: {e}")
            return False

    def _create_sample_data(self):
        """Create sample data for demonstration"""
        # Sample 51% attack data
        etc_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=1000, freq='H'),
            'block_height': range(1, 1001),
            'block_time': np.random.normal(12.5, 2, 1000),
            'difficulty': np.random.lognormal(20, 1, 1000),
            'is_51_attack': [1 if i % 50 == 0 else 0 for i in range(1000)]
        })
        etc_data.to_csv(f"{self.data_path}/etc_51_attack.csv", index=False)

        # Sample anomaly data
        anomaly_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=1000, freq='H'),
            'transaction_volume': np.random.lognormal(10, 2, 1000),
            'gas_price': np.random.exponential(20, 1000),
            'anomaly_type': ['normal' if i % 30 != 0 else 'attack' for i in range(1000)]
        })
        anomaly_data.to_csv(f"{self.data_path}/blockchain_anomalies.csv", index=False)

    def _extract_etc_features(self, etc_data):
        """Extract features from ETC dataset"""
        features = etc_data.copy()
        if 'is_51_attack' in features.columns:
            features['attack_detected'] = features['is_51_attack']
        return features

    def _extract_anomaly_features(self, anomaly_data):
        """Extract features from anomaly dataset"""
        features = anomaly_data.copy()
        features['is_anomaly'] = (features['anomaly_type'] == 'attack').astype(int)
        return features

    def preprocess_datasets(self):
        """Process and merge datasets"""
        print("🔄 Processing datasets...")
        try:
            etc_data = pd.read_csv(f"{self.data_path}/etc_51_attack.csv")
            anomaly_data = pd.read_csv(f"{self.data_path}/blockchain_anomalies.csv")

            etc_features = self._extract_etc_features(etc_data)
            anomaly_features = self._extract_anomaly_features(anomaly_data)

            # Merge datasets on timestamp
            merged_data = pd.merge(etc_features, anomaly_features, on='timestamp', how='inner')

            # Create final target variable
            merged_data['attack_detected'] = (
                    (merged_data.get('is_51_attack', 0) == 1) |
                    (merged_data.get('is_anomaly', 0) == 1)
            ).astype(int)

            # Save processed data
            merged_data.to_csv(f"{self.processed_path}/merged_blockchain_data.csv", index=False)
            print(f"✅ Datasets processed! {len(merged_data)} samples created.")
            return merged_data

        except Exception as e:
            print(f"❌ Dataset processing failed: {e}")
            return self._create_fallback_data()

    def _create_fallback_data(self):
        """Create fallback data if processing fails"""
        print("🔄 Creating fallback data...")
        fallback_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=500, freq='H'),
            'block_time': np.random.normal(12.5, 2, 500),
            'difficulty': np.random.lognormal(20, 1, 500),
            'transaction_volume': np.random.lognormal(10, 2, 500),
            'attack_detected': [1 if i % 25 == 0 else 0 for i in range(500)]
        })
        fallback_data.to_csv(f"{self.processed_path}/merged_blockchain_data.csv", index=False)
        return fallback_data


# Global instance
kaggle_integration = KaggleIntegration()