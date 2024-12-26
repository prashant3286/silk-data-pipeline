import logging
import requests
from typing import Dict, Any, List
from datetime import datetime
from src.models.host import Host
from src.config.settings import settings

class QualysClient:
    """
    Client for interacting with Qualys API to fetch host information
    """
    def __init__(self):
        self.api_token = settings.QUALYS_API_TOKEN
        self.base_url = settings.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'token': self.api_token,
            'accept': 'application/json'
        })
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_hosts(self, skip: int = 0, limit: int = 2) -> List[Dict[str, Any]]:
        """
        Fetch hosts from Qualys API with pagination
        
        :param skip: Number of records to skip
        :param limit: Number of records to fetch
        :return: List of raw host data
        """
        endpoint = "/api/qualys/hosts/get"
        url = f"{self.base_url}{endpoint}"
        params = {"skip": skip, "limit": limit}
        
        self.logger.info(f"Fetching hosts from URL: {url} with params: {params}")

        try:
            response = self.session.post(url, params=params, data='', timeout=settings.API_REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            # Assuming the API returns a list directly
            hosts = data if isinstance(data, list) else []
            self.logger.debug(f"Fetched hosts: {hosts}")
            return hosts
        
        except requests.RequestException as e:
            self.logger.error(f"Error fetching Qualys hosts: {e}")
            if e.response:
                self.logger.error(f"Response content: {e.response.content}")
            return []

    def normalize_host(self, raw_host: Dict[str, Any]) -> Host:
        """
        Convert raw Qualys host data to unified Host model
        
        :param raw_host: Raw host data from Qualys
        :return: Normalized Host object
        """
        try:
            return Host(
                source_system='Qualys',
                source_id=str(raw_host.get('id', '')),
                hostname=raw_host.get('hostname', ''),
                ip_addresses=[raw_host.get('ip_address', '')],
                mac_addresses=raw_host.get('mac_addresses', []),
                operating_system=raw_host.get('os', ''),
                os_version=raw_host.get('os_version', ''),
                first_seen=datetime.fromisoformat(
                    raw_host.get('first_seen', datetime.now().isoformat())
                ),
                last_seen=datetime.fromisoformat(
                    raw_host.get('last_seen', datetime.now().isoformat())
                ),
                vulnerability_count=raw_host.get('vulnerability_count', 0),
                raw_data=raw_host
            )
        except Exception as e:
            self.logger.warning(f"Could not normalize Qualys host: {e}")
            return None

    def get_normalized_hosts(self, limit: int = 2) -> List[Host]:
        """
        Get normalized hosts from Qualys
        
        :param limit: Number of hosts to fetch
        :return: List of normalized hosts
        """
        raw_hosts = []
        skip = 0
        
        while len(raw_hosts) < limit:
            batch = self.fetch_hosts(skip=skip, limit=limit)
            if not batch:
                break
            
            raw_hosts.extend(batch)
            skip += len(batch)
        
        normalized_hosts = [
            host for host in 
            (self.normalize_host(raw_host) for raw_host in raw_hosts[:limit]) 
            if host is not None
        ]
        
        return normalized_hosts