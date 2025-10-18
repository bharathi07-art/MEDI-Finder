from datetime import datetime, timezone
from models import db
import json

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    parsed_medicines = db.Column(db.Text, nullable=True)  # JSON string of parsed medicines
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', back_populates='prescriptions')

    def set_parsed_medicines(self, medicines_list):
        """Set parsed medicines as JSON string"""
        if medicines_list:
            self.parsed_medicines = json.dumps(medicines_list)
        else:
            self.parsed_medicines = None

    def get_parsed_medicines(self):
        """Get parsed medicines as list of dictionaries"""
        if self.parsed_medicines:
            try:
                return json.loads(self.parsed_medicines)
            except json.JSONDecodeError:
                return []
        return []

    def get_formatted_medicines(self):
        """Get formatted string of medicines for display"""
        medicines = self.get_parsed_medicines()
        if not medicines:
            return "No medicines extracted"

        formatted_lines = []
        for i, med in enumerate(medicines, 1):
            name = med.get('standardized_name', med.get('original_name', 'Unknown'))
            dosage = med.get('dosage', '')
            frequency = med.get('frequency', 'As directed')

            if dosage:
                formatted_lines.append(f"{i}. {name} {dosage} - {frequency}")
            else:
                formatted_lines.append(f"{i}. {name} - {frequency}")

        return "\n".join(formatted_lines)

    def has_medicines(self):
        """Check if prescription has extracted medicines"""
        return bool(self.get_parsed_medicines())
