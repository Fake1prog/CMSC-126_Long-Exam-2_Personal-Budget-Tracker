from django.db import models
from django.contrib.auth.models import User


class ErrorLog(models.Model):
    ERROR_TYPES = [
        ('VALIDATION', 'Validation Error'),
        ('PERMISSION', 'Permission Error'),
        ('SYSTEM', 'System Error'),
        ('DATABASE', 'Database Error'),
        ('OTHER', 'Other Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    error_type = models.CharField(max_length=20, choices=ERROR_TYPES)
    description = models.TextField()
    stack_trace = models.TextField(blank=True)
    user_action = models.TextField(blank=True, help_text="What was the user doing?")
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_error_type_display()} at {self.timestamp}"