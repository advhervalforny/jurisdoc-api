"""
Schemas do Sistema Jurídico Inteligente.

Schemas Pydantic para validação de entrada/saída da API.
"""

from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseListResponse,
    CaseWithDocumentsResponse,
    LegalAreaResponse,
    DocumentSummary,
)

from app.schemas.document import (
    DocumentCreate,
    DocumentStatusUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentWithVersionsResponse,
    DocumentVersionCreate,
    DocumentVersionResponse,
    DocumentVersionListResponse,
    PieceTypeResponse,
    VersionSummary,
)

from app.schemas.assertion import (
    AssertionCreate,
    AssertionBulkCreate,
    AssertionSourceLink,
    AssertionResponse,
    AssertionWithSourcesResponse,
    AssertionListResponse,
    AssertionBulkResponse,
    AssertionValidationResponse,
    SourceSummary,
)

from app.schemas.source import (
    SourceCreate,
    SourceResponse,
    SourceListResponse,
    SourceTypeInfo,
)

from app.schemas.rendering import (
    RenderRequest,
    RenderingResponse,
    RenderingListResponse,
)

__all__ = [
    # Case
    "CaseCreate",
    "CaseUpdate",
    "CaseResponse",
    "CaseListResponse",
    "CaseWithDocumentsResponse",
    "LegalAreaResponse",
    "DocumentSummary",
    
    # Document
    "DocumentCreate",
    "DocumentStatusUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentWithVersionsResponse",
    "DocumentVersionCreate",
    "DocumentVersionResponse",
    "DocumentVersionListResponse",
    "PieceTypeResponse",
    "VersionSummary",
    
    # Assertion
    "AssertionCreate",
    "AssertionBulkCreate",
    "AssertionSourceLink",
    "AssertionResponse",
    "AssertionWithSourcesResponse",
    "AssertionListResponse",
    "AssertionBulkResponse",
    "AssertionValidationResponse",
    "SourceSummary",
    
    # Source
    "SourceCreate",
    "SourceResponse",
    "SourceListResponse",
    "SourceTypeInfo",
    
    # Rendering
    "RenderRequest",
    "RenderingResponse",
    "RenderingListResponse",
]
