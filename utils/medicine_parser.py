import re
import logging
from typing import List, Dict, Tuple
import json

logger = logging.getLogger(__name__)

class MedicineParser:
    """Parses extracted text from prescriptions to identify medicines and their details"""

    # Common medicine name patterns
    MEDICINE_PATTERNS = [
        r'\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|units?|tablets?|capsules?|drops?)\b',
        r'\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg)\b',
        r'\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(tablets?|capsules?|drops?)\b',
    ]

    # Dosage frequency patterns
    FREQUENCY_PATTERNS = [
        r'(\d+)\s*time[s]?\s*(?:per|a|daily|day)',
        r'(\d+)\s*x\s*(?:per|a|daily|day)',
        r'(\d+)\s*times?\s*daily',
        r'(\d+)\s*tablets?\s*(?:per|a|daily|day)',
        r'(\d+)\s*capsules?\s*(?:per|a|daily|day)',
        r'once\s*daily',
        r'twice\s*daily',
        r'thrice\s*daily',
        r'every\s*(\d+)\s*hours?',
        r'(\d+)\s*hourly',
    ]

    # Duration patterns
    DURATION_PATTERNS = [
        r'for\s*(\d+)\s*days?',
        r'(\d+)\s*days?',
        r'for\s*(\d+)\s*weeks?',
        r'(\d+)\s*weeks?',
        r'for\s*(\d+)\s*months?',
        r'(\d+)\s*months?',
    ]

    def __init__(self):
        self.common_medicines = self._load_common_medicines()

    def _load_common_medicines(self) -> Dict[str, str]:
        """Load common medicine names and their standardized forms"""
        return {
            'paracetamol': 'Paracetamol',
            'acetaminophen': 'Paracetamol',
            'amoxicillin': 'Amoxicillin',
            'azithromycin': 'Azithromycin',
            'ibuprofen': 'Ibuprofen',
            'aspirin': 'Aspirin',
            'cetirizine': 'Cetirizine',
            'loratadine': 'Loratadine',
            'omeprazole': 'Omeprazole',
            'pantoprazole': 'Pantoprazole',
            'metformin': 'Metformin',
            'atorvastatin': 'Atorvastatin',
            'simvastatin': 'Simvastatin',
            'lisinopril': 'Lisinopril',
            'amlodipine': 'Amlodipine',
            'losartan': 'Losartan',
            'vitamin d': 'Vitamin D',
            'vitamin d3': 'Vitamin D3',
            'calcium': 'Calcium',
            'iron': 'Iron',
            'multivitamin': 'Multivitamin',
        }

    def parse_text(self, text: str) -> List[Dict]:
        """Parse prescription text and extract medicine information"""
        if not text or not text.strip():
            return []

        medicines = []
        lines = text.lower().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            medicine_info = self._parse_medicine_line(line)
            if medicine_info:
                medicines.append(medicine_info)

        # If no structured medicines found, try to extract general medicine names
        if not medicines:
            medicines = self._extract_medicine_names(text)

        return medicines

    def _parse_medicine_line(self, line: str) -> Dict | None:
        """Parse a single line for medicine information"""
        # Try to match medicine patterns
        for pattern in self.MEDICINE_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                medicine_name = match.group(1).strip()
                dosage = match.group(2) if len(match.groups()) > 1 else None

                # Standardize medicine name
                standardized_name = self._standardize_medicine_name(medicine_name)

                # Extract frequency
                frequency = self._extract_frequency(line)

                # Extract duration
                duration = self._extract_duration(line)

                return {
                    'original_name': medicine_name,
                    'standardized_name': standardized_name,
                    'dosage': dosage,
                    'frequency': frequency,
                    'duration': duration,
                    'raw_text': line.strip()
                }

        return None

    def _extract_medicine_names(self, text: str) -> List[Dict]:
        """Extract medicine names when structured parsing fails"""
        medicines = []

        # Look for common medicine names in the text
        for common_name, standard_name in self.common_medicines.items():
            if common_name in text.lower():
                # Try to find context around the medicine name
                context = self._get_medicine_context(text, common_name)

                medicines.append({
                    'original_name': common_name,
                    'standardized_name': standard_name,
                    'dosage': None,
                    'frequency': self._extract_frequency(context),
                    'duration': self._extract_duration(context),
                    'raw_text': context.strip()
                })

        return medicines

    def _get_medicine_context(self, text: str, medicine_name: str, context_window: int = 50) -> str:
        """Get context around a medicine name"""
        index = text.lower().find(medicine_name)
        if index == -1:
            return ""

        start = max(0, index - context_window)
        end = min(len(text), index + len(medicine_name) + context_window)

        return text[start:end]

    def _standardize_medicine_name(self, name: str) -> str:
        """Standardize medicine name using common names dictionary"""
        name_lower = name.lower().strip()

        # Direct match
        if name_lower in self.common_medicines:
            return self.common_medicines[name_lower]

        # Partial match
        for common_name, standard_name in self.common_medicines.items():
            if common_name in name_lower or name_lower in common_name:
                return standard_name

        # Return capitalized original if no match found
        return name.title()

    def _extract_frequency(self, text: str) -> str:
        """Extract dosage frequency from text"""
        for pattern in self.FREQUENCY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                frequency = match.group(1) if match.groups() else match.group(0)
                return frequency.strip()
        return "As directed"

    def _extract_duration(self, text: str) -> str:
        """Extract treatment duration from text"""
        for pattern in self.DURATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                duration = match.group(1) if match.groups() else match.group(0)
                return duration.strip()
        return "As directed"

    def format_medicine_info(self, medicines: List[Dict]) -> str:
        """Format medicine information for display"""
        if not medicines:
            return "No medicines could be extracted from the prescription."

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

# Utility function to get medicine parser instance
def get_medicine_parser():
    """Get medicine parser instance"""
    return MedicineParser()
