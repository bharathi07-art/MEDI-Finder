from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .medicine import Medicine
from .pharmacy import Pharmacy
from .availability import PharmacyMedicine
from .review import Review
from .prescription import Prescription
