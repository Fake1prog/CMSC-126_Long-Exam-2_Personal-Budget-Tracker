# conftest.py
import os
import sys
import django
from django.conf import settings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CMSC_126_Long_Exam_2_Personal_Budget_Tracker.settings')
django.setup()