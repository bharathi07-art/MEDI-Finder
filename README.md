# Medi-Finder

A comprehensive pharmacy finder web application built with Flask that helps users locate medicines and pharmacies in their area while providing pharmacy administrators with tools to manage their inventory.

## 🚀 Features

### For Users (Customers)
- **Medicine Search**: Search for medicines by name or generic name
- **Location-Based Search**: Find nearby pharmacies using geolocation
- **Real-Time Availability**: Check medicine stock and prices across pharmacies
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### For Pharmacy Administrators
- **Inventory Management**: Add, update, and manage medicine stock
- **Price Management**: Set and update medicine prices
- **Bulk Updates**: Efficiently update multiple medicines at once
- **Dashboard Analytics**: View stock statistics and pharmacy performance
- **Secure Access**: Role-based access control for pharmacy admins

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **ORM**: SQLAlchemy
- **Testing**: pytest
- **Deployment**: Ready for Heroku/AWS/GCP

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/medifinder.git
   cd medifinder
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📖 Usage

### For Customers
1. **Register/Login**: Create an account or log in to access full features
2. **Search Medicines**: Use the search bar to find medicines by name
3. **View Results**: Browse pharmacies, check prices, and see availability
4. **Get Directions**: Use integrated maps to navigate to pharmacies

### For Pharmacy Admins
1. **Register as Pharmacy**: Sign up with pharmacy details during registration
2. **Access Dashboard**: Log in to view your pharmacy dashboard
3. **Manage Inventory**: Add new medicines or update existing stock
4. **Update Prices**: Modify medicine prices as needed
5. **Monitor Statistics**: View inventory levels and performance metrics

## 🏗️ Project Structure

```
medifinder/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── medicine.py      # Medicine model
│   ├── pharmacy.py      # Pharmacy model
│   └── availability.py  # Medicine availability model
├── routes/               # Flask blueprints
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   ├── pharmacy.py      # Pharmacy management routes
│   └── search.py        # Search functionality routes
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── search.html      # Search results page
│   └── pharmacy/
│       ├── dashboard.html
│       └── update_stock.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── map.js       # Map functionality
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── helpers.py       # Helper functions
│   ├── geolocation.py   # Location services
│   └── sample_data.py   # Sample data for testing
└── tests/                # Test suite
    ├── __init__.py
    ├── conftest.py      # Test configuration
    ├── test_auth.py     # Authentication tests
    ├── test_pharmacy.py # Pharmacy tests
    ├── test_search.py   # Search tests
    └── test_frontend.py # Frontend tests
```

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_pharmacy.py

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Heroku Deployment
1. Create a Heroku app
2. Set environment variables in Heroku dashboard
3. Push to Heroku:
   ```bash
   git push heroku main
   ```

### Environment Variables
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

### Pharmacy Endpoints
- `GET /pharmacy/dashboard` - Pharmacy admin dashboard
- `POST /pharmacy/update-stock` - Update medicine stock
- `POST /pharmacy/bulk-update-stock` - Bulk update stock

### Search Endpoints
- `GET /api/search` - Search medicines and pharmacies
- `GET /api/pharmacies` - Get pharmacy list

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **CSRF Protection**: Cross-site request forgery protection
- **Role-Based Access**: Different permissions for customers and pharmacy admins
- **Input Validation**: Comprehensive form validation
- **SQL Injection Prevention**: Parameterized queries with SQLAlchemy

## 📊 Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- password (Hashed)
- name
- role (customer/pharmacy_admin)
- pharmacy_id (Foreign Key, nullable)

### Medicines Table
- id (Primary Key)
- name
- generic_name
- description

### Pharmacies Table
- id (Primary Key)
- name
- address
- latitude
- longitude
- contact_number
- is_verified

### PharmacyMedicine Table (Junction)
- id (Primary Key)
- pharmacy_id (Foreign Key)
- medicine_id (Foreign Key)
- price
- stock
- is_available
- last_updated

## 🐛 Known Issues & Future Enhancements

### Current Limitations
- SQLite database (consider PostgreSQL for production)
- Basic geolocation (can be enhanced with Google Maps API)
- No email notifications for low stock alerts

### Planned Features
- [ ] Mobile app development
- [ ] Advanced search filters
- [ ] Prescription upload and management
- [ ] Integration with insurance providers
- [ ] Real-time stock updates via WebSocket
- [ ] Multi-language support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [Your GitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Flask framework for the robust web framework
- Bootstrap for responsive UI components
- SQLAlchemy for excellent ORM capabilities
- All contributors and the open-source community

## 📞 Support

If you have any questions or need help, please open an issue on GitHub or contact the maintainers.

---

**Note**: This is a student project and is not intended for medical diagnosis or emergency use. Always consult healthcare professionals for medical advice.
