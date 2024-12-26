import logging
from typing import List, Dict, Any
from difflib import SequenceMatcher
from src.models.host import Host

class HostDeduplicator:
    """
    Service to deduplicate and merge hosts from multiple sources
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def compute_similarity_score(self, host1: Host, host2: Host) -> float:
        """
        Compute similarity score between two hosts
        
        :param host1: First host
        :param host2: Second host
        :return: Similarity score (0-1)
        """
        similarity_checks = [
            self._ip_address_similarity(host1, host2),
            self._mac_address_similarity(host1, host2),
            self._hostname_similarity(host1, host2),
            self._os_similarity(host1, host2)
        ]
        
        return sum(similarity_checks) / len(similarity_checks)

    def _ip_address_similarity(self, host1: Host, host2: Host) -> float:
        """
        Compute IP address similarity
        
        :param host1: First host
        :param host2: Second host
        :return: IP similarity score (0-1)
        """
        common_ips = set(host1.ip_addresses) & set(host2.ip_addresses)
        return len(common_ips) / max(len(host1.ip_addresses), len(host2.ip_addresses), 1)

    def _mac_address_similarity(self, host1: Host, host2: Host) -> float:
        """
        Compute MAC address similarity
        
        :param host1: First host
        :param host2: Second host
        :return: MAC similarity score (0-1)
        """
        common_macs = set(host1.mac_addresses) & set(host2.mac_addresses)
        return len(common_macs) / max(len(host1.mac_addresses), len(host2.mac_addresses), 1)

    def _hostname_similarity(self, host1: Host, host2: Host) -> float:
        """
        Compute hostname similarity using SequenceMatcher
        
        :param host1: First host
        :param host2: Second host
        :return: Hostname similarity score (0-1)
        """
        return SequenceMatcher(None, host1.hostname, host2.hostname).ratio()

    def _os_similarity(self, host1: Host, host2: Host) -> float:
        """
        Compute operating system similarity
        
        :param host1: First host
        :param host2: Second host
        :return: OS similarity score (0-1)
        """
        os_match = (
            host1.operating_system.lower() == host2.operating_system.lower() and
            host1.os_version.lower() == host2.os_version.lower()
        )
        return 1.0 if os_match else 0.0

    def deduplicate_hosts(
        self, 
        hosts: List[Host], 
        similarity_threshold: float = 0.7
    ) -> List[Host]:
        """
        Deduplicate hosts by merging similar hosts
        
        :param hosts: List of hosts to deduplicate
        :param similarity_threshold: Minimum similarity to consider hosts duplicates
        :return: Deduplicated list of hosts
        """
        deduplicated_hosts = []
        
        for host in hosts:
            duplicate_found = False
            
            for existing_host in deduplicated_hosts:
                similarity = self.compute_similarity_score(host, existing_host)
                
                if similarity >= similarity_threshold:
                    # Merge hosts if similar enough
                    merged_host = existing_host.merge(host)
                    deduplicated_hosts.remove(existing_host)
                    deduplicated_hosts.append(merged_host)
                    duplicate_found = True
                    break
            
            if not duplicate_found:
                deduplicated_hosts.append(host)
        
        self.logger.info(f"Deduplication reduced host count from {len(hosts)} to {len(deduplicated_hosts)}")
        return deduplicated_hosts