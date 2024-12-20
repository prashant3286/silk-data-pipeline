from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

@dataclass
class Host:
    """
    Unified host model representing normalized host information
    from multiple security scanning tools
    """
    # Unique identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_system: str = ''  # Qualys/Crowdstrike
    source_id: str = ''  # Original ID from source system

    # Host Identification Details
    hostname: str = ''
    ip_addresses: List[str] = field(default_factory=list)
    mac_addresses: List[str] = field(default_factory=list)

    # System Details
    operating_system: str = ''
    os_version: str = ''
    architecture: str = ''

    # Scan and Discovery Metadata
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    is_active: bool = True

    # Security Scan Details
    last_vulnerability_scan: Optional[datetime] = None
    vulnerability_count: int = 0

    # Raw data for reference
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Perform data validation and cleanup after initialization
        """
        # Ensure timestamps are datetime objects
        if isinstance(self.first_seen, str):
            self.first_seen = datetime.fromisoformat(self.first_seen)
        if isinstance(self.last_seen, str):
            self.last_seen = datetime.fromisoformat(self.last_seen)
        
        # Deduplicate lists
        self.ip_addresses = list(set(filter(None, self.ip_addresses)))
        self.mac_addresses = list(set(filter(None, self.mac_addresses)))

    def merge(self, other: 'Host') -> 'Host':
        """
        Merge two host records, preferring non-empty/more recent data
        
        :param other: Another Host object to merge with
        :return: Merged Host object
        """
        merged_data = asdict(self)
        
        # Merge strategies for different fields
        merged_data['ip_addresses'] = list(set(self.ip_addresses + other.ip_addresses))
        merged_data['mac_addresses'] = list(set(self.mac_addresses + other.mac_addresses))
        
        # Prefer non-empty string values
        for field in ['hostname', 'operating_system', 'os_version', 'architecture']:
            merged_data[field] = (
                self.__dict__.get(field) or 
                other.__dict__.get(field)
            )
        
        # Use most recent timestamps
        merged_data['first_seen'] = min(
            self.first_seen or datetime.max, 
            other.first_seen or datetime.max
        )
        merged_data['last_seen'] = max(
            self.last_seen or datetime.min, 
            other.last_seen or datetime.min
        )
        
        # Aggregate vulnerability information
        merged_data['vulnerability_count'] = max(
            self.vulnerability_count, 
            other.vulnerability_count
        )
        
        # Combine raw data
        merged_data['raw_data'] = {**self.raw_data, **other.raw_data}
        
        # Prefer the first source system 
        merged_data['source_system'] = (
            self.source_system or 
            other.source_system
        )
        
        return Host(**merged_data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Host object to dictionary
        
        :return: Dictionary representation of the Host
        """
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip_addresses': self.ip_addresses,
            'mac_addresses': self.mac_addresses,
            'operating_system': self.operating_system,
            'os_version': self.os_version,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'vulnerability_count': self.vulnerability_count,
            'source_system': self.source_system
        }