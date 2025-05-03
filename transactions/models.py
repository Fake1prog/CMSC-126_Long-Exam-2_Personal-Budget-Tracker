from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
from django.core.validators import MinValueValidator
from decimal import Decimal


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    title = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"{self.title} - {self.amount:.2f} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        # Ensure category type matches transaction type
        if self.category and self.category.type != self.type:
            # Try to find a matching category or create default
            try:
                self.category = Category.objects.get(
                    user=self.user,
                    type=self.type,
                    name='Other'
                )
            except Category.DoesNotExist:
                # Create a default category
                self.category = Category.objects.create(
                    user=self.user,
                    name='Other',
                    type=self.type,
                    is_default=True
                )

        super().save(*args, **kwargs)