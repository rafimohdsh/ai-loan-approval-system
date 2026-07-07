import requests
from typing import Optional, Dict, Any
from config.settings import settings

BASE_URL = f"http://{settings.API_HOST}:{settings.API_PORT}"


class APIClient:
    @staticmethod
    def get_health() -> Dict[str, Any]:
        """Check API health."""
        response = requests.get(f"{BASE_URL}/health")
        return response.json()

    @staticmethod
    def create_loan_application(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new loan application."""
        response = requests.post(f"{BASE_URL}/loans/applications", json=data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_loan_application(application_id: str) -> Dict[str, Any]:
        """Get a loan application."""
        response = requests.get(f"{BASE_URL}/loans/applications/{application_id}")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def list_loan_applications(
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """List loan applications."""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        response = requests.get(f"{BASE_URL}/loans/applications", params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def process_loan_application(application_id: str) -> Dict[str, Any]:
        """Trigger loan processing workflow."""
        response = requests.post(f"{BASE_URL}/loans/applications/{application_id}/process")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_loan_stats() -> Dict[str, Any]:
        """Get loan statistics."""
        response = requests.get(f"{BASE_URL}/loans/stats")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def submit_approval_decision(
        application_id: str,
        decision_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit approval decision."""
        response = requests.post(
            f"{BASE_URL}/loans/applications/{application_id}/decision",
            json=decision_data
        )
        response.raise_for_status()
        return response.json()
