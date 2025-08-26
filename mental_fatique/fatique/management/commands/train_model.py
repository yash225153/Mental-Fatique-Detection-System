"""
Management command to train the fatigue detection model using pre-existing dataset.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from fatique.ml_models.fatigue_detector import FatigueDetector

class Command(BaseCommand):
    help = 'Train the fatigue detection model using pre-existing dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            type=str,
            default='default',
            help='Name of the dataset to use for training'
        )
        parser.add_argument(
            '--epochs',
            type=int,
            default=100,
            help='Number of training epochs'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=32,
            help='Batch size for training'
        )

    def handle(self, *args, **options):
        dataset_name = options['dataset']
        epochs = options['epochs']
        batch_size = options['batch_size']

        self.stdout.write(f"Training model using dataset: {dataset_name}")
        
        # Initialize detector
        detector = FatigueDetector()
        
        # Train model
        history = detector.train(
            dataset_name=dataset_name,
            epochs=epochs,
            batch_size=batch_size
        )
        
        # Evaluate model
        metrics = detector.evaluate(dataset_name=dataset_name)
        
        # Save model
        model_dir = os.path.join(settings.BASE_DIR, 'fatique', 'ml_models', 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f'fatigue_detector_{dataset_name}.h5')
        detector.save_model(model_path)
        
        # Save training history
        history_path = os.path.join(model_dir, f'training_history_{dataset_name}.json')
        with open(history_path, 'w') as f:
            json.dump(history.history, f)
        
        # Print results
        self.stdout.write(self.style.SUCCESS(f"Model trained successfully!"))
        self.stdout.write(f"Model saved to: {model_path}")
        self.stdout.write(f"Training history saved to: {history_path}")
        
        self.stdout.write("\nEvaluation metrics:")
        self.stdout.write(f"Accuracy: {metrics['accuracy']:.4f}")
        self.stdout.write(f"Precision: {metrics['precision']:.4f}")
        self.stdout.write(f"Recall: {metrics['recall']:.4f}")
        self.stdout.write(f"F1 Score: {metrics['f1_score']:.4f}")
        
        self.stdout.write("\nConfusion Matrix:")
        for row in metrics['confusion_matrix']:
            self.stdout.write(str(row))
        
        # Print training history
        self.stdout.write("\nTraining history:")
        for epoch, (loss, val_loss, acc, val_acc) in enumerate(zip(
            history.history['loss'],
            history.history['val_loss'],
            history.history['accuracy'],
            history.history['val_accuracy']
        )):
            self.stdout.write(
                f"Epoch {epoch + 1}: "
                f"loss={loss:.4f}, val_loss={val_loss:.4f}, "
                f"acc={acc:.4f}, val_acc={val_acc:.4f}"
            ) 