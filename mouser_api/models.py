"""
Modelos de dados simplificados para a API Mouser
"""

from typing import Dict, List, Optional, Any

class TechnicalData:
    """Modelo consolidado com dados técnicos para seus agentes"""
    
    def __init__(
        self,
        part_number: str,
        manufacturer: str,
        description: str,
        datasheet_url: Optional[str] = None,
        image_url: Optional[str] = None,
        category: Optional[str] = None,
        availability: Optional[str] = None,
        rohs_status: Optional[str] = None,
        specifications: Optional[Dict[str, str]] = None,
        product_url: Optional[str] = None
    ):
        self.part_number = part_number
        self.manufacturer = manufacturer
        self.description = description
        self.datasheet_url = datasheet_url
        self.image_url = image_url
        self.category = category
        self.availability = availability
        self.rohs_status = rohs_status
        self.specifications = specifications or {}
        self.product_url = product_url
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'part_number': self.part_number,
            'manufacturer': self.manufacturer,
            'description': self.description,
            'datasheet_url': self.datasheet_url,
            'image_url': self.image_url,
            'category': self.category,
            'availability': self.availability,
            'rohs_status': self.rohs_status,
            'specifications': self.specifications,
            'product_url': self.product_url
        }