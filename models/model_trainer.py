import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import logging
from datetime import datetime
from .feature_engineering import FeatureEngineer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import os
import traceback
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_trainer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        logger.info("Initializing ModelTrainer")
        self.model = None
        self.label_encoders = {}
        self.features = [
            'historical_price', 'price_tunisianet', 'price_mytech',
            'historical_discount', 'price_diff_competitors',
            'price_ratio_competitors', 'discount_impact', 'category_encoded'
        ]
        self.load_model()

    def _setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger('ModelTrainer')
        logger.setLevel(logging.INFO)
        
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('model_training.log')
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(log_format)
        f_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
        return logger
    
    def prepare_data(self, df, target_column):
        """Prepare data for training"""
        try:
            # Preprocess the data
            processed_df = self.feature_engineer.preprocess_data(df)
            
            # Split features and target
            X = processed_df.drop(columns=[target_column])
            y = processed_df[target_column]
            
            # Split into train and test sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            self.logger.error(f"Error in data preparation: {str(e)}")
            raise
    
    def train_model(self, X_train, y_train):
        """Train the model based on the specified model type"""
        try:
            if self.model_type == 'random_forest':
                from sklearn.ensemble import RandomForestRegressor
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=None,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    random_state=42
                )
            elif self.model_type == 'xgboost':
                from xgboost import XGBRegressor
                self.model = XGBRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=7,
                    random_state=42
                )
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            self.model.fit(X_train, y_train)
            self.logger.info(f"Model training completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in model training: {str(e)}")
            raise
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate the model performance"""
        try:
            y_pred = self.model.predict(X_test)
            
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            metrics = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'r2': r2
            }
            
            self.logger.info(f"Model evaluation metrics: {metrics}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error in model evaluation: {str(e)}")
            raise
    
    def save_model(self, model_path, encoders_path):
        """Save the trained model and encoders"""
        try:
            # Save the model
            joblib.dump(self.model, model_path)
            
            # Save the feature engineering encoders
            self.feature_engineer.save_encoders(encoders_path)
            
            self.logger.info(f"Model and encoders saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self):
        """Load the trained model and encoders"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'trained_model.joblib')
            encoders_path = os.path.join(os.path.dirname(__file__), 'encoders.joblib')
            
            logger.info(f"Looking for model files at: {model_path} and {encoders_path}")
            
            if os.path.exists(model_path) and os.path.exists(encoders_path):
                logger.info("Found model files, loading...")
                self.model = joblib.load(model_path)
                self.label_encoders = joblib.load(encoders_path)
                logger.info("Model and encoders loaded successfully")
            else:
                logger.warning("Model files not found, initializing new model")
                self.initialize_new_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.error(traceback.format_exc())
            self.initialize_new_model()

    def initialize_new_model(self):
        """Initialize a new model if loading fails"""
        try:
            logger.info("Initializing new RandomForest model")
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.label_encoders = {}
            
            # Create a simple training dataset
            X = pd.DataFrame({
                'historical_price': [100, 200, 300],
                'price_tunisianet': [110, 210, 310],
                'price_mytech': [105, 205, 305],
                'historical_discount': [0, 0.1, 0.2],
                'price_diff_competitors': [5, 5, 5],
                'price_ratio_competitors': [1.05, 1.05, 1.05],
                'discount_impact': [0, 20, 60],
                'category_encoded': [0, 1, 2]
            })
            y = np.array([100, 200, 300])
            
            # Train the model
            self.model.fit(X, y)
            logger.info("New model initialized and trained with sample data")
            
            # Save the model
            model_path = os.path.join(os.path.dirname(__file__), 'trained_model.joblib')
            encoders_path = os.path.join(os.path.dirname(__file__), 'encoders.joblib')
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.label_encoders, encoders_path)
            logger.info("New model saved successfully")
            
        except Exception as e:
            logger.error(f"Error initializing new model: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def preprocess_input(self, data):
        """Preprocess input data for prediction"""
        try:
            logger.info("Preprocessing input data")
            # Create a copy of the input data
            df = data.copy()
            
            # Clean and convert price columns
            price_columns = ['historical_price', 'price_tunisianet', 'price_mytech', 'historical_discount']
            for col in price_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    logger.warning(f"Missing price column: {col}, setting to 0")
                    df[col] = 0
            
            # Calculate price differences and ratios
            df['price_diff_competitors'] = df['price_tunisianet'] - df['price_mytech']
            df['price_ratio_competitors'] = df['price_tunisianet'] / df['price_mytech'].replace(0, 1)
            df['discount_impact'] = df['historical_discount'] * df['historical_price']
            
            # Encode categorical variables
            if 'category' in df.columns:
                if 'category' not in self.label_encoders:
                    logger.info("Creating new category encoder")
                    self.label_encoders['category'] = LabelEncoder()
                    df['category'] = df['category'].fillna('unknown')
                    self.label_encoders['category'].fit(df['category'])
                df['category_encoded'] = self.label_encoders['category'].transform(df['category'])
            else:
                logger.warning("Missing category column, setting category_encoded to 0")
                df['category_encoded'] = 0
            
            # Ensure all required features are present
            for feature in self.features:
                if feature not in df.columns:
                    logger.warning(f"Missing feature: {feature}, setting to 0")
                    df[feature] = 0
            
            logger.debug(f"Preprocessed data: {df[self.features].to_dict()}")
            return df[self.features]
        except Exception as e:
            logger.error(f"Error preprocessing input data: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def predict(self, data):
        """Make predictions using the trained model"""
        try:
            logger.info("Making predictions")
            if self.model is None:
                logger.error("Model not loaded or initialized")
                raise ValueError("Model not loaded or initialized")
            
            # Preprocess input data
            processed_data = self.preprocess_input(data)
            
            # Make predictions
            predictions = self.model.predict(processed_data)
            logger.info(f"Raw predictions: {predictions}")
            
            # Apply business rules
            predictions = np.where(
                predictions < data['historical_price'].values * 0.9,
                data['historical_price'].values * 0.9,
                predictions
            )
            
            logger.info(f"Final predictions after business rules: {predictions}")
            return predictions
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def train(self, data):
        """Train the model on new data"""
        try:
            logger.info("Training model on new data")
            # Preprocess training data
            processed_data = self.preprocess_input(data)
            
            # Train model
            self.model.fit(processed_data, data['price'])
            
            # Save model and encoders
            model_path = os.path.join(os.path.dirname(__file__), 'trained_model.joblib')
            encoders_path = os.path.join(os.path.dirname(__file__), 'encoders.joblib')
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.label_encoders, encoders_path)
            
            logger.info("Model trained and saved successfully")
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            logger.error(traceback.format_exc())
            raise 