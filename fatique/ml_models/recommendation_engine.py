"""
Recommendation engine for productivity boosting using reinforcement learning.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os
import joblib
import random
from django.utils import timezone
from ..models import ProductivityRecommendation, FatigueAnalysis, ProductivitySession
from .data_preprocessor import DataPreprocessor

class RecommendationEngine:
    def __init__(self, model_path=None):
        """
        Initialize the recommendation engine.
        
        Args:
            model_path: Path to a saved model file
        """
        self.model = None
        self.preprocessor = DataPreprocessor()
        self.recommendation_types = [
            'break',
            'exercise',
            'meditation',
            'task_switch',
            'environment',
            'nutrition'
        ]
        
        # Define model architecture
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self._build_model()
    
    def _build_model(self):
        """Build the neural network model for reinforcement learning."""
        # Input shape: 14 features (same as fatigue detector) + 1 for fatigue score
        model = Sequential([
            Dense(32, activation='relu', input_shape=(15,)),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dropout(0.2),
            Dense(len(self.recommendation_types), activation='softmax')  # Output: recommendation probabilities
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
    
    def train(self, states, actions, rewards, epochs=50, batch_size=32):
        """
        Train the model using reinforcement learning.
        
        Args:
            states: Array of state vectors
            actions: Array of action indices
            rewards: Array of rewards
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        if self.model is None:
            self._build_model()
        
        # Convert actions to one-hot encoding
        action_one_hot = tf.keras.utils.to_categorical(
            actions, num_classes=len(self.recommendation_types)
        )
        
        # Weight actions by rewards
        weighted_actions = action_one_hot * np.expand_dims(rewards, axis=1)
        
        # Train the model
        history = self.model.fit(
            states, weighted_actions,
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        return history
    
    def get_recommendation(self, user, fatigue_analysis=None):
        """
        Get a productivity recommendation for a user.
        
        Args:
            user: User to recommend for
            fatigue_analysis: Optional fatigue analysis, will fetch latest if None
            
        Returns:
            Dictionary with recommendation details
        """
        # Get fatigue analysis if not provided
        if fatigue_analysis is None:
            fatigue_analysis = FatigueAnalysis.objects.filter(user=user).order_by('-timestamp').first()
            
            if fatigue_analysis is None:
                # If no fatigue analysis exists, return a random recommendation
                return self._get_random_recommendation(user)
        
        # Prepare state vector
        self.preprocessor.fit(user=user, time_window=24)
        state = self.preprocessor.prepare_features(user, time_window=24)
        
        # Add fatigue score to state
        fatigue_score = fatigue_analysis.fatigue_score / 100.0  # Normalize to 0-1
        state = np.append(state, fatigue_score).reshape(1, -1)
        
        if self.model is None:
            # If no model exists, return a random recommendation
            return self._get_random_recommendation(user)
        
        # Get recommendation probabilities
        probs = self.model.predict(state)[0]
        
        # Choose recommendation type based on probabilities
        # We can either choose the highest probability or sample from the distribution
        if random.random() < 0.8:  # 80% of the time choose the best recommendation
            rec_index = np.argmax(probs)
        else:  # 20% of the time explore other options
            rec_index = np.random.choice(len(self.recommendation_types), p=probs)
        
        rec_type = self.recommendation_types[rec_index]
        
        # Generate recommendation details based on type and fatigue level
        recommendation = self._generate_recommendation(user, rec_type, fatigue_analysis)
        
        return recommendation
    
    def _get_random_recommendation(self, user):
        """Generate a random recommendation when no model is available."""
        rec_type = random.choice(self.recommendation_types)
        
        # Get the latest fatigue analysis if available
        fatigue_analysis = FatigueAnalysis.objects.filter(user=user).order_by('-timestamp').first()
        
        return self._generate_recommendation(user, rec_type, fatigue_analysis)
    
    def _generate_recommendation(self, user, rec_type, fatigue_analysis):
        """
        Generate a detailed recommendation based on type and fatigue level.
        
        Args:
            user: User to recommend for
            rec_type: Type of recommendation
            fatigue_analysis: Fatigue analysis object
            
        Returns:
            Dictionary with recommendation details
        """
        fatigue_level = fatigue_analysis.fatigue_level if fatigue_analysis else 'moderate'
        
        # Define recommendation templates based on type and fatigue level
        templates = {
            'break': {
                'low': {
                    'description': "Take a short 5-minute break to refresh your mind.",
                    'duration': 5,
                    'expected_impact': 0.1
                },
                'moderate': {
                    'description': "Take a 10-minute break and step away from your screen.",
                    'duration': 10,
                    'expected_impact': 0.2
                },
                'high': {
                    'description': "Take a 15-minute break, preferably outside or in a different environment.",
                    'duration': 15,
                    'expected_impact': 0.3
                },
                'severe': {
                    'description': "Take a 30-minute break. Consider a power nap if possible.",
                    'duration': 30,
                    'expected_impact': 0.4
                }
            },
            'exercise': {
                'low': {
                    'description': "Do some light stretching for 5 minutes to improve circulation.",
                    'duration': 5,
                    'expected_impact': 0.15
                },
                'moderate': {
                    'description': "Take a 10-minute walk or do some desk exercises.",
                    'duration': 10,
                    'expected_impact': 0.25
                },
                'high': {
                    'description': "Do a 15-minute moderate exercise session (brisk walk, yoga, etc.).",
                    'duration': 15,
                    'expected_impact': 0.35
                },
                'severe': {
                    'description': "Take a 20-minute break for physical activity - a walk outside is ideal.",
                    'duration': 20,
                    'expected_impact': 0.45
                }
            },
            'meditation': {
                'low': {
                    'description': "Take 3 minutes for deep breathing exercises.",
                    'duration': 3,
                    'expected_impact': 0.1
                },
                'moderate': {
                    'description': "Do a 5-minute guided meditation or mindfulness exercise.",
                    'duration': 5,
                    'expected_impact': 0.2
                },
                'high': {
                    'description': "Take 10 minutes for a guided meditation session.",
                    'duration': 10,
                    'expected_impact': 0.3
                },
                'severe': {
                    'description': "Do a 15-minute meditation session focusing on stress reduction.",
                    'duration': 15,
                    'expected_impact': 0.4
                }
            },
            'task_switch': {
                'low': {
                    'description': "Switch to a different, less demanding task for a while.",
                    'duration': 30,
                    'expected_impact': 0.1
                },
                'moderate': {
                    'description': "Change your current task to something that requires different mental resources.",
                    'duration': 45,
                    'expected_impact': 0.2
                },
                'high': {
                    'description': "Switch to a completely different type of work that engages different parts of your brain.",
                    'duration': 60,
                    'expected_impact': 0.3
                },
                'severe': {
                    'description': "Take on a creative or enjoyable task that feels less like work for the next hour.",
                    'duration': 60,
                    'expected_impact': 0.4
                }
            },
            'environment': {
                'low': {
                    'description': "Adjust your workspace - clean up clutter or adjust lighting.",
                    'duration': 5,
                    'expected_impact': 0.1
                },
                'moderate': {
                    'description': "Change your environment - move to a different room or space.",
                    'duration': 10,
                    'expected_impact': 0.2
                },
                'high': {
                    'description': "Work from a completely different location for a while, like a cafe or common area.",
                    'duration': 15,
                    'expected_impact': 0.3
                },
                'severe': {
                    'description': "Take your work outside or to a stimulating environment for a change of scenery.",
                    'duration': 30,
                    'expected_impact': 0.4
                }
            },
            'nutrition': {
                'low': {
                    'description': "Drink a glass of water and have a small healthy snack.",
                    'duration': 5,
                    'expected_impact': 0.1
                },
                'moderate': {
                    'description': "Take a proper break to hydrate and have a nutritious snack like nuts or fruit.",
                    'duration': 10,
                    'expected_impact': 0.2
                },
                'high': {
                    'description': "Take time for a proper meal with protein and complex carbohydrates.",
                    'duration': 20,
                    'expected_impact': 0.3
                },
                'severe': {
                    'description': "Take a full break for a balanced meal and make sure you're well hydrated.",
                    'duration': 30,
                    'expected_impact': 0.4
                }
            }
        }
        
        # Get recommendation template
        template = templates.get(rec_type, {}).get(fatigue_level, {
            'description': f"Take a break and do something to refresh your mind.",
            'duration': 15,
            'expected_impact': 0.2
        })
        
        # Create and save recommendation
        recommendation = ProductivityRecommendation.objects.create(
            user=user,
            recommendation_type=rec_type,
            description=template['description'],
            expected_impact=template['expected_impact'],
            duration=template['duration'],
            timestamp=timezone.now()
        )
        
        return {
            'id': recommendation.id,
            'type': rec_type,
            'description': template['description'],
            'duration': template['duration'],
            'expected_impact': template['expected_impact'] * 100  # Convert to percentage
        }
    
    def update_model(self, user, recommendation_id, effectiveness):
        """
        Update the model based on user feedback.
        
        Args:
            user: User who received the recommendation
            recommendation_id: ID of the recommendation
            effectiveness: User-reported effectiveness (0-1)
            
        Returns:
            True if model was updated, False otherwise
        """
        try:
            # Get the recommendation
            recommendation = ProductivityRecommendation.objects.get(id=recommendation_id)
            
            # Update the recommendation with user feedback
            recommendation.implemented = True
            recommendation.effectiveness = effectiveness
            recommendation.save()
            
            # Get the state at the time of recommendation
            fatigue_analysis = FatigueAnalysis.objects.filter(
                user=user,
                timestamp__lte=recommendation.timestamp
            ).order_by('-timestamp').first()
            
            if fatigue_analysis is None:
                return False
            
            # Prepare state vector
            self.preprocessor.fit(user=user, time_window=24)
            state = self.preprocessor.prepare_features(user, time_window=24)
            
            # Add fatigue score to state
            fatigue_score = fatigue_analysis.fatigue_score / 100.0  # Normalize to 0-1
            state = np.append(state, fatigue_score).reshape(1, -1)
            
            # Get action index
            action_index = self.recommendation_types.index(recommendation.recommendation_type)
            
            # Use effectiveness as reward
            reward = effectiveness
            
            # Update model with this single example
            self.train(
                states=state,
                actions=np.array([action_index]),
                rewards=np.array([reward]),
                epochs=1,
                batch_size=1
            )
            
            return True
        except Exception as e:
            print(f"Error updating model: {e}")
            return False
    
    def save_model(self, model_path):
        """Save the model to a file."""
        if self.model is None:
            raise ValueError("No model to save")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save the model
        self.model.save(model_path)
        
        # Save the preprocessor
        preprocessor_path = os.path.join(
            os.path.dirname(model_path),
            'recommendation_preprocessor.joblib'
        )
        joblib.dump(self.preprocessor, preprocessor_path)
    
    def load_model(self, model_path):
        """Load the model from a file."""
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found: {model_path}")
        
        # Load the model
        self.model = load_model(model_path)
        
        # Load the preprocessor
        preprocessor_path = os.path.join(
            os.path.dirname(model_path),
            'recommendation_preprocessor.joblib'
        )
        
        if os.path.exists(preprocessor_path):
            self.preprocessor = joblib.load(preprocessor_path)
        else:
            self.preprocessor = DataPreprocessor()
