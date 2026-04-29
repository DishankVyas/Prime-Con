from config import settings
from abc import ABC, abstractmethod

class SAPConnector(ABC):
    @abstractmethod
    def execute_query(self, sql_or_query: str) -> list[dict]: ...

class MockSQLiteConnector(SAPConnector):
    def execute_query(self, sql: str) -> list[dict]:
        from sqlalchemy import text
        from database import get_session
        with get_session() as s:
            result = s.execute(text(sql))
            cols = list(result.keys())
            return [dict(zip(cols, row)) for row in result.fetchall()]

class SAPECCConnector(SAPConnector):
    """Stub for real SAP ECC via PyRFC. Set SAP_HOST, SAP_CLIENT, SAP_USER, SAP_PASSWORD in .env"""
    def execute_query(self, function_module: str) -> list[dict]:
        raise NotImplementedError("PyRFC connector not yet implemented. Set MOCK_MODE=false and configure SAP credentials.")

class SAPS4HANAConnector(SAPConnector):
    """Stub for SAP S/4HANA via OData v4. Set S4_BASE_URL, S4_API_KEY in .env"""
    def execute_query(self, odata_path: str) -> list[dict]:
        raise NotImplementedError("OData v4 connector not yet implemented.")

def get_connector() -> SAPConnector:
    if settings.MOCK_MODE:
        return MockSQLiteConnector()
    connector_type = getattr(settings, 'SAP_CONNECTOR_TYPE', 'mock')
    if connector_type == 'ecc':
        return SAPECCConnector()
    elif connector_type == 's4':
        return SAPS4HANAConnector()
    return MockSQLiteConnector()
