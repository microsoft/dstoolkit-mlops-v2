from src.invoice_processing.predict_component.predict.data_extraction.extractors.base_extractor import (
    Extractor
)
from src.invoice_processing.predict_component.predict.data_extraction.models.extraction_response import (
    ExtractionResponse,
    Invoice,
    Provider,
    ServiceFor
)


class MockExtractor(Extractor):

    def extract_data(self, file) -> ExtractionResponse:
        invoice = Invoice(
            lineItems=[],
            provider=Provider(
                name="Mock Provider"
            ),
            serviceFor=ServiceFor(
                name="Mock Patient"
            ),
            totalClaimAmount=1.99
        )

        return ExtractionResponse(
            invoice=invoice,
            metadata={}
        )
