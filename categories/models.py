from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    CATEGORY_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    color = models.CharField(max_length=7, default='#7CB9E8')  # Default light blue color
    icon = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def soft_delete(self):
        # Check for transactions
        if hasattr(self, 'transaction_set') and self.transaction_set.exists():
            self.name = f"[Archived] {self.name}"
            self.is_active = False
            self.save()
            return True
        else:
            # No transactions, safe to hard delete
            self.delete()
            return True

    def get_html_attributes(self):
        """Return HTML attributes for use in dropdown menus."""
        return f'data-type="{self.type}" data-color="{self.color}" data-icon="{self.icon}"'