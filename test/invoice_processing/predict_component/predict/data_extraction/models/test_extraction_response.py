import unittest
from pydantic import ValidationError

from src.invoice_processing.predict_component.predict.data_extraction.models.extraction_response import (
    ExtractionResponse
)


class TestExtractionResponse(unittest.TestCase):
    def setUp(self):
        self.valid_line_item = {
            "amount": 100.0,
            "text": "Consultation",
            "transactionType": "Service",
            "serviceStartDate": "2023-01-01",
            "serviceEndDate": "2023-01-02"
        }
        self.valid_invoice = {
            "totalClaimAmount": 100.0,
            "provider": {
                "name": "Provider A"
            },
            "serviceFor": {
                "name": "Patient A"
            },
            "lineItems": [self.valid_line_item]
        }
        self.valid_invoice_data = {
            "invoice": self.valid_invoice
        }

    def test_valid_invoice_data(self):
        invoice_data = ExtractionResponse(**self.valid_invoice_data)
        self.assertEqual(invoice_data.invoice.totalClaimAmount, 100.0)
        self.assertEqual(invoice_data.invoice.provider.name, "Provider A")
        self.assertEqual(invoice_data.invoice.serviceFor.name, "Patient A")
        self.assertEqual(len(invoice_data.invoice.lineItems), 1)
        self.assertEqual(invoice_data.invoice.lineItems[0].amount, 100.0)

    def test_invalid_invoice_data(self):
        invalid_invoice_data = self.valid_invoice_data.copy()
        invalid_invoice_data["invoice"]["totalClaimAmount"] = "invalid_amount"
        with self.assertRaises(ValidationError):
            ExtractionResponse(**invalid_invoice_data)

    def test_missing_required_field(self):
        invalid_invoice_data = self.valid_invoice_data.copy()
        del invalid_invoice_data["invoice"]["provider"]["name"]
        with self.assertRaises(ValidationError):
            ExtractionResponse(**invalid_invoice_data)


if __name__ == '__main__':
    unittest.main()
