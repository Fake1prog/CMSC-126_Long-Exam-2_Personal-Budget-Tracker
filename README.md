# GastadorCheck: Personal Budget Tracker

GastadorCheck is a comprehensive web-based personal budget tracking application built with Django. It helps users manage their finances by tracking income and expenses, setting budgets, categorizing transactions, and providing insightful financial reports.

### Live Demo

You can visit the live application at:
[https://cmsc-126-long-exam-2-personal-budget.onrender.com](https://cmsc-126-long-exam-2-personal-budget.onrender.com)

## 🌟 Features

**1. Account & Setup**
- Create an account and set your preferences

**2. Dashboard**
- See financial summary with income, expenses, and balance
- View recent transactions at a glance
- Visualize spending with interactive charts

**3. Transactions**
- Record income and expenses quickly
- Search and filter transactions by date, amount, or category
- Add notes to keep track of details

**4. Categories**
- Organize finances with color-coded categories
- Create custom categories with icons
- Separate tracking for income and expense types

**5. Budgets**
- Set spending limits for different categories
- Track budget progress with visual indicators
- Define budget periods (weekly, monthly, yearly)

**6. Reports**
- Generate monthly financial summaries
- Analyze spending by category over time
- Download charts and visualizations as images

**7. Data Export**
- Export transactions to CSV format
- Select custom date ranges for export
- One-click export for quick sharing

**8. Responsive Design**
- Access from any device (desktop, tablet, mobile)
- Consistent experience across all screen sizes

## 📋 Requirements

- Python 3.11 or higher
- Django 5.2
- Other dependencies are listed in `requirements.txt`

## 🚀 Installation & Setup

### Local Development

1. **Clone the repository**
   ```
   git clone <copy our repository-url>
   cd GastadorCheck
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root and add the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

5. **Run migrations**
   ```
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and go to:
   ```
   http://127.0.0.1:8000/
   ```

### Deployment Options

#### Render

The project is configured for deployment on Render.

1. **Create a new Web Service on Render**
   - Connect the GitHub repository
   - Set the build command: `./build.sh`
   - Set the start command: `gunicorn CMSC_126_Long_Exam_2_Personal_Budget_Tracker.wsgi:application`
   - Add environment variables (SECRET_KEY, DEBUG, etc.)





## 💡 User Guide

### Getting Started

1. **Register a new account** or log in with existing credentials
2. Upon registration, default categories will be created automatically
3. Navigate through the application using the top menu

### Managing Transactions

1. **Add Transactions**
   - Click "Add Income" or "Add Expense" from the dashboard
   - Fill in the transaction details including title, amount, date, and category
   - Add optional notes for reference

2. **View Transactions**
   - Access the Transactions page from the main menu
   - Use filters to search by title, amount range, date range, type, or category

3. **Edit or Delete Transactions**
   - Click "Edit" or "Delete" next to any transaction in the list

### Working with Categories

1. **Create Custom Categories**
   - Navigate to the Categories page
   - Click "Add Category"
   - Choose a name, type (Income/Expense), color, and optional icon

2. **Manage Categories**
   - Edit category details or delete unused categories
   - Categories with transactions will be archived rather than permanently deleted

### Setting Budgets

1. **Create a Budget**
   - Go to the Budgets page
   - Click "Add Budget"
   - Select a category, set an amount and period (weekly, monthly, yearly)
   - Specify start and optional end dates

2. **Track Budget Progress**
   - View your budget usage on the Budgets page
   - Visual indicators show when you're approaching or exceeding budget limits

### Viewing Reports

1. **Dashboard**
   - See an overview of your financial situation
   - View income vs. expenses and category breakdowns

2. **Monthly Reports**
   - Navigate to Reports > Monthly Report
   - Select a month to view detailed income and expense breakdown

3. **Category Reports**
   - Go to Reports > Category Report
   - Filter by category and date range
   - View spending trends over time

4. **Export Data**
   - From any report page, click "Export Data"
   - Choose date range for export
   - Download a CSV file of your transactions

## 🧪 Testing
Follow these steps to run the tests on your local machine:

### Prerequisites

1. **Install testing dependencies**
   ```
   pip install pytest pytest-django
   ```

2. **Ensure you have activated your virtual environment**
   ```
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

### Running Tests

1. **Run all tests**
   ```
   pytest
   ```

2. **Run tests with verbose output**
   ```
   pytest -v
   ```

3. **Run tests for a specific app**
   ```
   pytest core/
   pytest users/
   pytest transactions/
   ```

4. **Run a specific test file**
   ```
   pytest core/tests.py
   ```

5. **Run a specific test class or function**
   ```
   pytest core/tests.py::test_dashboard_view_logged_in
   ```

### Test Configuration

The project uses pytest.ini and conftest.py to properly configure Django integration:
- pytest.ini sets the Django settings module and test file patterns
- conftest.py ensures proper path configuration and Django initialization

If you add new test files, follow the existing naming pattern (tests.py or test_*.py) and the test discovery will find them automatically.

### Coverage Report

To generate a test coverage report:

1. **Install coverage tools**
   ```
   pip install pytest-cov
   ```

2. **Run tests with coverage**
   ```
   pytest --cov=.
   ```

3. **Generate an HTML coverage report**
   ```
   pytest --cov=. --cov-report=html
   ```
   This will create a `htmlcov` directory - open `htmlcov/index.html` in your browser to view the report.

## 🛠️ Technical Details

- **Frontend**: HTML, Tailwind CSS, AlpineJS
- **Backend**: Django 5.2
- **Database**: SQLite (default), configurable for other databases
- **Charts**: ApexCharts
- **Date Picker**: Flatpickr

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
