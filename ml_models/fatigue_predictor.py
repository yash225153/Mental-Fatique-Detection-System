"""
Mental Fatigue Prediction ML Model
This module contains machine learning models for predicting mental fatigue
based on typing patterns, mouse movements, and facial analysis data.
"""

import numpy as np
import json
from datetime import datetime
import os

class FatiguePredictor:
    """
    A machine learning model for predicting mental fatigue levels
    based on multiple input modalities.
    """
    
    def __init__(self):
        self.model_weights = {
            'typing': {
                'speed_weight': 0.3,
                'error_weight': 0.4,
                'pause_weight': 0.3
            },
            'mouse': {
                'reaction_weight': 0.4,
                'accuracy_weight': 0.3,
                'score_weight': 0.3
            },
            'facial': {
                'blink_weight': 0.3,
                'closure_weight': 0.4,
                'expression_weight': 0.3
            }
        }
        
        # Normalization parameters (learned from training data)
        self.normalization_params = {
            'typing_speed': {'mean': 45, 'std': 15},
            'error_rate': {'mean': 5, 'std': 3},
            'pause_frequency': {'mean': 3, 'std': 2},
            'reaction_time': {'mean': 600, 'std': 200},
            'mouse_accuracy': {'mean': 70, 'std': 20},
            'mouse_score': {'mean': 8, 'std': 4},
            'blink_rate': {'mean': 20, 'std': 8},
            'eye_closure': {'mean': 200, 'std': 100}
        }
    
    def normalize_feature(self, value, feature_name):
        """Normalize a feature using z-score normalization."""
        params = self.normalization_params.get(feature_name, {'mean': 0, 'std': 1})
        return (value - params['mean']) / params['std']
    
    def predict_typing_fatigue(self, typing_data):
        """
        Predict fatigue level based on typing patterns.
        
        Args:
            typing_data (dict): Dictionary containing typing metrics
            
        Returns:
            float: Fatigue score (0-100)
        """
        if not typing_data:
            return 45  # Default moderate fatigue
        
        # Extract and normalize features
        speed = typing_data.get('typingSpeed', 45)
        error_rate = typing_data.get('errorRate', 5)
        pause_freq = typing_data.get('pauseFrequency', 3)
        
        # Normalize features
        norm_speed = self.normalize_feature(speed, 'typing_speed')
        norm_error = self.normalize_feature(error_rate, 'error_rate')
        norm_pause = self.normalize_feature(pause_freq, 'pause_frequency')
        
        # Calculate fatigue indicators
        speed_fatigue = max(0, -norm_speed * 20 + 30)  # Lower speed = higher fatigue
        error_fatigue = max(0, norm_error * 25 + 20)   # Higher errors = higher fatigue
        pause_fatigue = max(0, norm_pause * 20 + 15)   # More pauses = higher fatigue
        
        # Weighted combination
        weights = self.model_weights['typing']
        fatigue_score = (
            speed_fatigue * weights['speed_weight'] +
            error_fatigue * weights['error_weight'] +
            pause_fatigue * weights['pause_weight']
        )
        
        return min(max(fatigue_score, 0), 100)
    
    def predict_mouse_fatigue(self, mouse_data):
        """
        Predict fatigue level based on mouse movement patterns.
        
        Args:
            mouse_data (dict): Dictionary containing mouse metrics
            
        Returns:
            float: Fatigue score (0-100)
        """
        if not mouse_data:
            return 45  # Default moderate fatigue
        
        # Extract and normalize features
        reaction_time = mouse_data.get('reactionTime', 600)
        accuracy = mouse_data.get('accuracy', 70)
        score = mouse_data.get('score', 8)
        
        # Normalize features
        norm_reaction = self.normalize_feature(reaction_time, 'reaction_time')
        norm_accuracy = self.normalize_feature(accuracy, 'mouse_accuracy')
        norm_score = self.normalize_feature(score, 'mouse_score')
        
        # Calculate fatigue indicators
        reaction_fatigue = max(0, norm_reaction * 25 + 20)  # Slower reaction = higher fatigue
        accuracy_fatigue = max(0, -norm_accuracy * 20 + 25)  # Lower accuracy = higher fatigue
        score_fatigue = max(0, -norm_score * 15 + 20)  # Lower score = higher fatigue
        
        # Weighted combination
        weights = self.model_weights['mouse']
        fatigue_score = (
            reaction_fatigue * weights['reaction_weight'] +
            accuracy_fatigue * weights['accuracy_weight'] +
            score_fatigue * weights['score_weight']
        )
        
        return min(max(fatigue_score, 0), 100)
    
    def predict_facial_fatigue(self, facial_data):
        """
        Predict fatigue level based on facial analysis.
        
        Args:
            facial_data (dict): Dictionary containing facial metrics
            
        Returns:
            float: Fatigue score (0-100)
        """
        if not facial_data:
            return 45  # Default moderate fatigue
        
        # Extract and normalize features
        blink_rate = facial_data.get('blinkRate', 20)
        eye_closure = facial_data.get('eyeClosure', 200)
        expression = facial_data.get('expression', 'Neutral')
        
        # Normalize features
        norm_blink = self.normalize_feature(blink_rate, 'blink_rate')
        norm_closure = self.normalize_feature(eye_closure, 'eye_closure')
        
        # Calculate fatigue indicators
        # Very low or very high blink rates indicate fatigue
        blink_fatigue = max(0, abs(norm_blink) * 15 + 10)
        closure_fatigue = max(0, norm_closure * 20 + 15)  # Longer closures = higher fatigue
        
        # Expression-based fatigue
        expression_fatigue = {
            'Tired': 40,
            'Distracted': 25,
            'Focused': 10,
            'Neutral': 15
        }.get(expression, 15)
        
        # Weighted combination
        weights = self.model_weights['facial']
        fatigue_score = (
            blink_fatigue * weights['blink_weight'] +
            closure_fatigue * weights['closure_weight'] +
            expression_fatigue * weights['expression_weight']
        )
        
        return min(max(fatigue_score, 0), 100)
    
    def predict_combined_fatigue(self, typing_data, mouse_data, facial_data):
        """
        Predict overall fatigue level using all available data modalities.
        
        Args:
            typing_data (dict): Typing pattern data
            mouse_data (dict): Mouse movement data
            facial_data (dict): Facial analysis data
            
        Returns:
            dict: Combined prediction results
        """
        # Get individual predictions
        typing_fatigue = self.predict_typing_fatigue(typing_data)
        mouse_fatigue = self.predict_mouse_fatigue(mouse_data)
        facial_fatigue = self.predict_facial_fatigue(facial_data)
        
        # Calculate weights based on data availability and quality
        weights = []
        scores = []
        
        if typing_data and typing_data.get('typingSpeed', 0) > 0:
            weights.append(0.35)
            scores.append(typing_fatigue)
        
        if mouse_data and mouse_data.get('score', 0) > 0:
            weights.append(0.35)
            scores.append(mouse_fatigue)
        
        if facial_data and facial_data.get('analyzed', False):
            weights.append(0.30)
            scores.append(facial_fatigue)
        
        # Calculate weighted average
        if weights:
            # Normalize weights to sum to 1
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            combined_score = sum(s * w for s, w in zip(scores, normalized_weights))
        else:
            combined_score = 45  # Default moderate fatigue
        
        # Apply ensemble correction (slight adjustment based on consistency)
        score_variance = np.var(scores) if len(scores) > 1 else 0
        if score_variance > 400:  # High variance indicates uncertainty
            combined_score = combined_score * 0.9 + 45 * 0.1  # Regress toward mean
        
        return {
            'combined_fatigue_score': min(max(combined_score, 0), 100),
            'individual_scores': {
                'typing': typing_fatigue,
                'mouse': mouse_fatigue,
                'facial': facial_fatigue
            },
            'confidence': max(0, 1 - score_variance / 1000),
            'data_quality': {
                'typing_available': bool(typing_data and typing_data.get('typingSpeed', 0) > 0),
                'mouse_available': bool(mouse_data and mouse_data.get('score', 0) > 0),
                'facial_available': bool(facial_data and facial_data.get('analyzed', False))
            }
        }
    
    def get_recommendations(self, fatigue_score, individual_scores=None):
        """
        Generate personalized recommendations based on fatigue analysis.
        
        Args:
            fatigue_score (float): Overall fatigue score
            individual_scores (dict): Individual modality scores
            
        Returns:
            dict: Recommendations and insights
        """
        recommendations = []
        insights = []
        
        # General recommendations based on overall fatigue
        if fatigue_score < 30:
            recommendations.append({
                'type': 'Continue',
                'action': 'Keep working',
                'description': 'Your fatigue level is low. You can continue your current activity.',
                'duration': 'N/A',
                'priority': 'low'
            })
        elif fatigue_score < 50:
            recommendations.append({
                'type': 'Short Break',
                'action': 'Take a 5-minute break',
                'description': 'Stand up, stretch, and rest your eyes for a few minutes.',
                'duration': '5 minutes',
                'priority': 'medium'
            })
        elif fatigue_score < 70:
            recommendations.append({
                'type': 'Break',
                'action': 'Take a 15-minute break',
                'description': 'Step away from your screen and do some light physical activity.',
                'duration': '15 minutes',
                'priority': 'high'
            })
        else:
            recommendations.append({
                'type': 'Extended Break',
                'action': 'Take a 30-minute break',
                'description': 'Consider a short nap, meditation, or light exercise.',
                'duration': '30 minutes',
                'priority': 'urgent'
            })
        
        # Specific recommendations based on individual scores
        if individual_scores:
            if individual_scores.get('typing', 0) > 60:
                recommendations.append({
                    'type': 'Typing Rest',
                    'action': 'Rest your hands',
                    'description': 'Your typing patterns show signs of fatigue. Take a break from typing.',
                    'duration': '10 minutes',
                    'priority': 'medium'
                })
                insights.append('High typing fatigue detected - consider ergonomic improvements')
            
            if individual_scores.get('mouse', 0) > 60:
                recommendations.append({
                    'type': 'Hand Rest',
                    'action': 'Rest your mouse hand',
                    'description': 'Your mouse reaction time and accuracy show signs of fatigue.',
                    'duration': '5 minutes',
                    'priority': 'medium'
                })
                insights.append('Mouse performance degradation detected')
            
            if individual_scores.get('facial', 0) > 60:
                recommendations.append({
                    'type': 'Eye Rest',
                    'action': 'Rest your eyes',
                    'description': 'Your facial analysis shows signs of visual fatigue.',
                    'duration': '10 minutes',
                    'priority': 'high'
                })
                insights.append('Visual fatigue detected - follow the 20-20-20 rule')
        
        return {
            'recommendations': recommendations,
            'insights': insights,
            'fatigue_level': self._get_fatigue_level_text(fatigue_score),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_fatigue_level_text(self, score):
        """Convert fatigue score to text description."""
        if score < 30:
            return 'Low'
        elif score < 50:
            return 'Moderate'
        elif score < 70:
            return 'High'
        else:
            return 'Severe'
    
    def save_session_data(self, session_data, filename=None):
        """Save session data for future analysis and model improvement."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'session_data_{timestamp}.json'
        
        # Create data directory if it doesn't exist
        os.makedirs('data/sessions', exist_ok=True)
        
        filepath = os.path.join('data/sessions', filename)
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return filepath

# Global model instance
fatigue_model = FatiguePredictor()

def predict_fatigue(typing_data=None, mouse_data=None, facial_data=None):
    """
    Convenience function for fatigue prediction.
    
    Args:
        typing_data (dict): Typing pattern data
        mouse_data (dict): Mouse movement data
        facial_data (dict): Facial analysis data
        
    Returns:
        dict: Prediction results
    """
    return fatigue_model.predict_combined_fatigue(typing_data, mouse_data, facial_data)

def get_recommendations(fatigue_score, individual_scores=None):
    """
    Convenience function for getting recommendations.
    
    Args:
        fatigue_score (float): Overall fatigue score
        individual_scores (dict): Individual modality scores
        
    Returns:
        dict: Recommendations and insights
    """
    return fatigue_model.get_recommendations(fatigue_score, individual_scores)
