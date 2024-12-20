import pytest
from datetime import datetime
from src.models.host import Host
from src.services.deduplication import HostDeduplicator

def create_test_host(
    hostname='test-host', 
    ip_addresses=None, 
    mac_addresses=None, 
    os='Windows', 
    os_version='10'
):
    return Host(
        hostname=hostname,
        ip_addresses=ip_addresses or [],
        mac_addresses=mac_addresses or [],
        operating_system=os,
        os_version=os_version,
        first_seen=datetime.now(),
        last_seen=datetime.now()
    )

def test_ip_address_similarity():
    deduplicator = HostDeduplicator()
    
    host1 = create_test_host(ip_addresses=['192.168.1.1'])
    host2 = create_test_host(ip_addresses=['192.168.1.1', '10.0.0.1'])
    host3 = create_test_host(ip_addresses=['10.0.0.2'])
    
    assert deduplicator._ip_address_similarity(host1, host2) == 1.0
    assert deduplicator._ip_address_similarity(host1, host3) == 0.0

def test_mac_address_similarity():
    deduplicator = HostDeduplicator()
    
    host1 = create_test_host(mac_addresses=['00:11:22:33:44:55'])
    host2 = create_test_host(mac_addresses=['00:11:22:33:44:55', '66:77:88:99:AA:BB'])
    host3 = create_test_host(mac_addresses=['AA:BB:CC:DD:EE:FF'])
    
    assert deduplicator._mac_address_similarity(host1, host2) == 1.0
    assert deduplicator._mac_address_similarity(host1, host3) == 0.0

def test_hostname_similarity():
    deduplicator = HostDeduplicator()
    
    host1 = create_test_host(hostname='server1')
    host2 = create_test_host(hostname='server1-prod')
    host3 = create_test_host(hostname='different-host')
    
    assert deduplicator._hostname_similarity(host1, host2) > 0.5
    assert deduplicator._hostname_similarity(host1, host3) < 0.5

def test_os_similarity():
    deduplicator = HostDeduplicator()
    
    host1 = create_test_host(os='Windows', os_version='10')
    host2 = create_test_host(os='Windows', os_version='10')
    host3 = create_test_host(os='Linux', os_version='Ubuntu')
    
    assert deduplicator._os_similarity(host1, host2) == 1.0
    assert deduplicator._os_similarity(host1, host3) == 0.0

def test_compute_similarity_score():
    deduplicator = HostDeduplicator()
    
    host1 = create_test_host(
        hostname='server1', 
        ip_addresses=['192.168.1.1'],
        mac_addresses=['00:11:22:33:44:55']
    )
    
    host2 = create_test_host(
        hostname='server1-prod', 
        ip_addresses=['192.168.1.1'],
        mac_addresses=['00:11:22:33:44:55']
    )
    
    host3 = create_test_host(
        hostname='different-host', 
        ip_addresses=['10.0.0.1'],
        mac_addresses=['AA:BB:CC:DD:EE:FF']
    )
    
    similarity1_2 = deduplicator.compute_similarity_score(host1, host2)
    similarity1_3 = deduplicator.compute_similarity_score(host1, host3)
    
    assert similarity1_2 > 0.7
    assert similarity1_3 < 0.5

def test_deduplicate_hosts():
    deduplicator = HostDeduplicator()
    
    hosts = [
        create_test_host(hostname='server1', ip_addresses=['192.168.1.1']),
        create_test_host(hostname='server1-prod', ip_addresses=['192.168.1.1']),
        create_test_host(hostname='completely-different', ip_addresses=['10.0.0.1'])
    ]
    
    deduplicated_hosts = deduplicator.deduplicate_hosts(hosts)
    
    assert len(deduplicated_hosts) == 2