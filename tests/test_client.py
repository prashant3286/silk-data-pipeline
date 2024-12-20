import pytest
from unittest.mock import patch, MagicMock
from src.clients.qualys_client import QualysClient
from src.clients.crowdstrike_client import CrowdstrikeClient

class TestQualysClient:
    @patch('requests.Session.post')
    def test_fetch_hosts(self, mock_post):
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'hosts': [
                {
                    'id': '1',
                    'hostname': 'test-host',
                    'ip_addresses': ['192.168.1.1'],
                    'os': 'Windows',
                    'os_version': '10'
                }
            ]
        }
        mock_post.return_value = mock_response

        client = QualysClient()
        hosts = client.fetch_hosts()

        assert len(hosts) == 1
        assert hosts[0]['hostname'] == 'test-host'

    def test_normalize_host(self):
        client = QualysClient()
        raw_host = {
            'id': '1',
            'hostname': 'test-host',
            'ip_addresses': ['192.168.1.1'],
            'os': 'Windows',
            'os_version': '10',
            'first_seen': '2024-01-01T00:00:00',
            'last_seen': '2024-01-02T00:00:00'
        }

        normalized_host = client.normalize_host(raw_host)

        assert normalized_host.hostname == 'test-host'
        assert normalized_host.operating_system == 'Windows'
        assert normalized_host.source_system == 'Qualys'

class TestCrowdstrikeClient:
    @patch('requests.Session.post')
    def test_fetch_hosts(self, mock_post):
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'hosts': [
                {
                    'cid': '1',
                    'hostname': 'crowdstrike-host',
                    'local_ip': ['10.0.0.1'],
                    'platform_name': 'Linux',
                    'platform_version': 'Ubuntu 20.04'
                }
            ]
        }
        mock_post.return_value = mock_response

        client = CrowdstrikeClient()
        hosts = client.fetch_hosts()

        assert len(hosts) == 1
        assert hosts[0]['hostname'] == 'crowdstrike-host'

    def test_normalize_host(self):
        client = CrowdstrikeClient()
        raw_host = {
            'cid': '1',
            'hostname': 'crowdstrike-host',
            'local_ip': ['10.0.0.1'],
            'platform_name': 'Linux',
            'platform_version': 'Ubuntu 20.04',
            'first_seen': '2024-01-01T00:00:00',
            'last_seen': '2024-01-02T00:00:00'
        }

        normalized_host = client.normalize_host(raw_host)

        assert normalized_host.hostname == 'crowdstrike-host'
        assert normalized_host.operating_system == 'Linux'
        assert normalized_host.source_system == 'Crowdstrike'