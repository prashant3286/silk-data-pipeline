import logging
from typing import Dict, Any, List
from datetime import datetime
import requests

from ..models.host import Host
from ..config.settings import settings

class CrowdstrikeClient:
    """
    Client for interacting with Crowdstrike API to fetch host information
    """
    def __init__(self, api_token: str = None):
        self.api_token = "armis-login@armis.com_60974105-5053-4267-b16e-392e8165c89a"
        self.base_url = "https://api.recruiting.app.silk.security/api/crowdstrike/hosts/get?skip=0&limit=2"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_hosts(self, skip: int = 0, limit: int = 2) -> List[Dict[str, Any]]:
        """
        Fetch hosts from Crowdstrike API with pagination
        
        :param skip: Number of records to skip
        :param limit: Number of records to fetch
        :return: List of raw host data
        """
        # endpoint = "/api/crowdstrike/hosts/get?skip=0&limit=2"
        
        try:
            response = self.session.post(
                f"{self.base_url}", 
                json={
                    "skip": skip,
                    "limit": limit
                },
                timeout=settings.API_REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('hosts', [])
        
        except requests.RequestException as e:
            self.logger.error(f"Error fetching Crowdstrike hosts: {e}")
            return []

    def normalize_host(self, raw_host: Dict[str, Any]) -> Host:
        """
        Convert raw Crowdstrike host data to unified Host model
        
        :param raw_host: Raw host data from Crowdstrike
        :return: Normalized Host object
        """
        try:
            return Host(
                source_system='Crowdstrike',
                source_id=str(raw_host.get('cid', '')),
                hostname=raw_host.get('hostname', ''),
                ip_addresses=raw_host.get('local_ip', []) + raw_host.get('external_ip', []),
                mac_addresses=raw_host.get('mac_addresses', []),
                operating_system=raw_host.get('platform_name', ''),
                os_version=raw_host.get('platform_version', ''),
                first_seen=datetime.fromisoformat(
                    raw_host.get('first_seen', datetime.now().isoformat())
                ),
                last_seen=datetime.fromisoformat(
                    raw_host.get('last_seen', datetime.now().isoformat())
                ),
                vulnerability_count=raw_host.get('active_vulnerabilities', 0),
                raw_data=raw_host
            )
        except Exception as e:
            self.logger.warning(f"Could not normalize Crowdstrike host: {e}")
            return None

    def get_normalized_hosts(self, limit: int = 2) -> List[Host]:
        """
        Get normalized hosts from Crowdstrike
        
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