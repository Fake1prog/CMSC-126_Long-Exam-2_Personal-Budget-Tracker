from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
from django.core.validators import MinValueValidator
from decimal import Decimal
from transactions.models import Transaction
from django.db.models import Sum
import logging

class Budget(models.Model):
    PERIOD_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='MONTHLY')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__name']

    def __str__(self):
        return f"{self.category.name} Budget: {self.amount} ({self.get_period_display()})"

    def calculate_spent(self, start_date=None, end_date=None):
        """Calculate how much has been spent under this budget for a given period"""


        logger = logging.getLogger(__name__)

        if not start_date:
            start_date = self.start_date
        if not end_date:
            from datetime import date
            end_date = date.today()

        # More detailed query with logging
        transactions = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='EXPENSE',
            date__gte=start_date,
            date__lte=end_date
        )

        # Debug logging
        logger.debug(f"Budget ID {self.id} for {self.category.name}:")
        logger.debug(f"Date range: {start_date} to {end_date}")
        logger.debug(f"Found {transactions.count()} matching transactions")

        for t in transactions:
            logger.debug(f"Transaction: {t.title}, Amount: {t.amount}, Date: {t.date}")

        total = sum(t.amount for t in transactions)
        logger.debug(f"Total spent: {total}")

        return total

    def calculate_remaining(self, start_date=None, end_date=None):
        """Calculate remaining budget"""
        spent = self.calculate_spent(start_date, end_date)
        return self.amount - spent

    def is_over_budget(self, start_date=None, end_date=None):
        """Check if over budget"""
        return self.calculate_remaining(start_date, end_date) < 0