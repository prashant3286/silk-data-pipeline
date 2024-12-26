import re
from typing import Dict, Any

class HostNormalizer:
    """
    Service to normalize host data from different sources
    """
    @staticmethod
    def normalize_hostname(hostname: str) -> str:
        """
        Normalize hostname by removing domain and converting to lowercase
        
        :param hostname: Input hostname
        :return: Normalized hostname
        """
        # Remove domain if present
        hostname = hostname.split('.')[0]
        return hostname.lower().strip()

    @staticmethod
    def normalize_ip(ip: str) -> str:
        """
        Validate and normalize IP address
        
        :param ip: Input IP address
        :return: Normalized IP address or empty string
        """
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, ip):
            return ip.strip()
        return ''

    @staticmethod
    def normalize_mac(mac: str) -> str:
        """
        Normalize MAC address
        
        :param mac: Input MAC address
        :return: Normalized MAC address
        """
        # Remove separators and convert to lowercase
        mac = re.sub(r'[.:-]', '', mac.lower())
        
        # Validate MAC address format
        mac_pattern = r'^([0-9a-f]{12})$'
        if re.match(mac_pattern, mac):
            return ':'.join(mac[i:i+2] for i in range(0, 12, 2))
        return ''

    @classmethod
    def normalize_host_data(cls, raw_host: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize various host data attributes
        
        :param raw_host: Raw host data
        :return: Normalized host data
        """
        normalized_data = raw_host.copy()
        
        # Normalize hostname
        if 'hostname' in normalized_data:
            normalized_data['hostname'] = cls.normalize_hostname(
                normalized_data['hostname']
            )
        
        # Normalize IP addresses
        if 'ip_addresses' in normalized_data:
            normalized_data['ip_addresses'] = [
                cls.normalize_ip(ip) for ip in normalized_data.get('ip_addresses', [])
                if cls.normalize_ip(ip)
            ]
        
        # Normalize MAC addresses
        if 'mac_addresses' in normalized_data:
            normalized_data['mac_addresses'] = [
                cls.normalize_mac(mac) for mac in normalized_data.get('mac_addresses', [])
                if cls.normalize_mac(mac)
            ]
        
        return normalized_data