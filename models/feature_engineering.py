import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from datetime import datetime

class FeatureEngineer:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def preprocess_data(self, df):
        """Preprocess the input dataframe"""
        df = df.copy()
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Convert categorical variables
        df = self._encode_categorical_variables(df)
        
        # Create time-based features
        df = self._create_time_features(df)
        
        # Scale numerical features
        df = self._scale_numerical_features(df)
        
        return df
    
    def _handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        # Fill numerical columns with median
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        df[numerical_cols] = df[numerical_cols].fillna(df[numerical_cols].median())
        
        # Fill categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        df[categorical_cols] = df[categorical_cols].fillna(df[categorical_cols].mode().iloc[0])
        
        return df
    
    def _encode_categorical_variables(self, df):
        """Encode categorical variables using LabelEncoder"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[col] = self.label_encoders[col].transform(df[col])
        
        return df
    
    def _create_time_features(self, df):
        """Create time-based features from date columns"""
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        
        for col in date_columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_dayofweek'] = df[col].dt.dayofweek
        
        return df
    
    def _scale_numerical_features(self, df):
        """Scale numerical features using StandardScaler"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        df[numerical_cols] = self.scaler.fit_transform(df[numerical_cols])
        return df
    
    def save_encoders(self, path):
        """Save the encoders and scaler to disk"""
        import joblib
        encoders_dict = {
            'label_encoders': self.label_encoders,
            'scaler': self.scaler
        }
        joblib.dump(encoders_dict, path)
    
    def load_encoders(self, path):
        """Load the encoders and scaler from disk"""
        import joblib
        encoders_dict = joblib.load(path)
        self.label_encoders = encoders_dict['label_encoders']
        self.scaler = encoders_dict['scaler'] 