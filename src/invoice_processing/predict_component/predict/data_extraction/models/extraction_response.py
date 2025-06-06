from pydantic import BaseModel
from typing import Optional, List


class LineItem(BaseModel):
    """Represents a line item in a structured format."""
    amount: float
    text: str
    transactionType: str  # noqa: N815
    serviceStartDate: str  # noqa: N815
    serviceEndDate: str  # noqa: N815
    miles: Optional[int] = None


class Provider(BaseModel):
    """Represents a provider in a structured format."""
    name: str


class ServiceFor(BaseModel):
    """Represents the person the service was provided for in a structured format."""
    name: str


class Invoice(BaseModel):
    """Represents an invoice in a structured format."""
    totalClaimAmount: float  # noqa: N815
    provider: Provider
    serviceFor: ServiceFor  # noqa: N815
    lineItems: List[LineItem]  # noqa: N815


class ExtractionResponse(BaseModel):
    """Represents extracted data in a structured format."""
    invoice: Invoice
    metadata: Optional[dict] = None
