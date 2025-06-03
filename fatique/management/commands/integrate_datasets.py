"""
Management command to integrate facial, mouse, and keyboard datasets.
"""

from django.core.management.base import BaseCommand
from fatique.datasets.data_integrator import DataIntegrator

class Command(BaseCommand):
    help = 'Integrate facial, mouse, and keyboard datasets'

    def handle(self, *args, **options):
        self.stdout.write("Starting dataset integration...")
        
        # Initialize data integrator
        integrator = DataIntegrator()
        
        # Update default dataset with integrated data
        success = integrator.update_default_dataset()
        
        if success:
            self.stdout.write(self.style.SUCCESS("Dataset integration completed successfully!"))
        else:
            self.stdout.write(self.style.ERROR("Dataset integration failed!")) 