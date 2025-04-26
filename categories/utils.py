def create_default_categories(user):
    """Create default categories for a new user."""
    from .models import Category

    # Default expense categories with colors
    default_expense_categories = [
        {"name": "Food & Dining", "color": "#FF5733", "icon": "🍽️"},
        {"name": "Transportation", "color": "#33A1FF", "icon": "🚗"},
        {"name": "Housing", "color": "#A333FF", "icon": "🏠"},
        {"name": "Utilities", "color": "#FF33A8", "icon": "💡"},
        {"name": "Entertainment", "color": "#33FF57", "icon": "🎬"},
        {"name": "Shopping", "color": "#FFC733", "icon": "🛍️"},
        {"name": "Health & Wellness", "color": "#3DFF33", "icon": "🏥"},
        {"name": "Education", "color": "#334FFF", "icon": "📚"},
        {"name": "Groceries", "color": "#33FFD4", "icon": "🛒"},
        {"name": "Personal Care", "color": "#FF33F6", "icon": "✂️"},
        {"name": "Travel", "color": "#33FFBD", "icon": "✈️"},
        {"name": "Other", "color": "#A0A0A0", "icon": "📋"},
    ]

    # Default income categories with colors
    default_income_categories = [
        {"name": "Salary", "color": "#66BB6A", "icon": "💼"},
        {"name": "Freelance", "color": "#26C6DA", "icon": "💻"},
        {"name": "Investments", "color": "#AB47BC", "icon": "📈"},
        {"name": "Gifts", "color": "#EF5350", "icon": "🎁"},
        {"name": "Other", "color": "#78909C", "icon": "📋"},
    ]

    # Create expense categories
    for category_data in default_expense_categories:
        Category.objects.create(
            user=user,
            name=category_data["name"],
            type="EXPENSE",
            color=category_data["color"],
            icon=category_data["icon"],
            is_default=True,
        )

    # Create income categories
    for category_data in default_income_categories:
        Category.objects.create(
            user=user,
            name=category_data["name"],
            type="INCOME",
            color=category_data["color"],
            icon=category_data["icon"],
            is_default=True,
        )