import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PricePredictor:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.initialize_model()

    def initialize_model(self):
        try:
            # Load the model if it exists
            if os.path.exists('price_model.joblib'):
                logger.info("Loading existing price prediction model")
                self.model = joblib.load('price_model.joblib')
            else:
                logger.info("Creating new price prediction model")
                # Create a new model with default parameters
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
                
                # Create some initial training data
                initial_data = pd.DataFrame({
                    'historical_price': [1000, 2000, 3000],
                    'price_tunisianet': [1100, 2100, 3100],
                    'price_mytech': [1050, 2050, 3050],
                    'historical_discount': [0.1, 0.2, 0.15],
                    'price_diff_competitors': [50, 50, 50],
                    'price_ratio_competitors': [1.05, 1.02, 1.01],
                    'discount_impact': [100, 400, 450],
                    'category_encoded': [0, 0, 0]
                })
                
                # Train the model with initial data
                self.model.fit(initial_data, initial_data['historical_price'])
                
                # Save the model
                joblib.dump(self.model, 'price_model.joblib')
                logger.info("New model created and saved successfully")
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            # Create a basic model as fallback
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def clean_price(self, price):
        """Clean and convert price to float"""
        try:
            if isinstance(price, str):
                price = price.replace('DT', '').replace('\xa0', '').replace(',', '').strip()
                return float(price)
            return float(price)
        except (ValueError, TypeError):
            return np.nan

    def predict_price(self, title, description, category='electronics', input_price=None):
        try:
            logger.info(f"Predicting price for: {title}")
            logger.info(f"Description: {description}")
            logger.info(f"Category: {category}")
            logger.info(f"Input price: {input_price}")
            
            # Use input price as base if provided
            base_price = self.clean_price(input_price) if input_price is not None else 1000.0
            
            # Calculate competitor prices based on input price
            tunisianet_price = base_price * 1.1  # 10% higher
            mytech_price = base_price * 1.05    # 5% higher
            
            # Prepare features
            features = {
                'historical_price': base_price,
                'price_tunisianet': tunisianet_price,
                'price_mytech': mytech_price,
                'historical_discount': 0.1,   # Default value
                'price_diff_competitors': tunisianet_price - mytech_price,
                'price_ratio_competitors': tunisianet_price / mytech_price,
                'discount_impact': base_price * 0.1,  # 10% of base price
                'category_encoded': self.label_encoder.fit_transform([category])[0]
            }

            # Log features for debugging
            logger.info(f"Features used for prediction: {json.dumps(features, indent=2)}")

            # Convert features to DataFrame
            features_df = pd.DataFrame([features])

            # Make prediction
            predicted_price = float(self.model.predict(features_df)[0])
            logger.info(f"Raw predicted price: {predicted_price}")

            # Apply business rules
            if predicted_price < base_price * 0.8:  # Don't go below 80% of input price
                predicted_price = base_price * 0.8
            elif predicted_price > base_price * 1.5:  # Don't go above 150% of input price
                predicted_price = base_price * 1.5

            # Round to 2 decimal places
            final_price = round(predicted_price, 2)
            logger.info(f"Final predicted price: {final_price}")

            return final_price

        except Exception as e:
            logger.error(f"Error predicting price: {str(e)}")
            logger.error(f"Error details: {str(e.__class__.__name__)}")
            # Return input price if prediction fails
            return self.clean_price(input_price) if input_price is not None else 1000.0

    def update_model(self, new_data):
        """Update the model with new data"""
        try:
            logger.info("Updating price prediction model")
            
            # Prepare features and target
            features = ['historical_price', 'price_tunisianet', 'price_mytech', 
                       'historical_discount', 'price_diff_competitors',
                       'price_ratio_competitors', 'discount_impact', 'category_encoded']
            
            X = new_data[features]
            y = new_data['price']

            # Update the model
            self.model.fit(X, y)

            # Save the updated model
            joblib.dump(self.model, 'price_model.joblib')
            logger.info("Model updated successfully")

        except Exception as e:
            logger.error(f"Error updating model: {str(e)}")

# Create a singleton instance
price_predictor = PricePredictor() 