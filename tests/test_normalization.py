import pytest
from src.services.normalization import HostNormalizer

def test_normalize_hostname():
    test_cases = [
        ('server1.example.com', 'server1'),
        ('DESKTOP-ABC123.local', 'desktop-abc123'),
        ('  Hostname with Spaces  ', 'hostname with spaces')
    ]

    for input_hostname, expected in test_cases:
        assert HostNormalizer.normalize_hostname(input_hostname) == expected

def test_normalize_ip():
    test_cases = [
        ('192.168.1.1', '192.168.1.1'),
        ('10.0.0.1', '10.0.0.1'),
        ('invalid.ip', ''),
        ('256.1.2.3', '')
    ]

    for input_ip, expected in test_cases:
        assert HostNormalizer.normalize_ip(input_ip) == expected

def test_normalize_mac():
    test_cases = [
        ('00:11:22:33:44:55', '00:11:22:33:44:55'),
        ('00-11-22-33-44-55', '00:11:22:33:44:55'),
        ('001122334455', '00:11:22:33:44:55'),
        ('invalid-mac', '')
    ]

    for input_mac, expected in test_cases:
        assert HostNormalizer.normalize_mac(input_mac) == expected

def test_normalize_host_data():
    raw_host = {
        'hostname': 'server1.example.com',
        'ip_addresses': ['192.168.1.1', 'invalid.ip'],
        'mac_addresses': ['00:11:22:33:44:55', 'invalid-mac']
    }

    normalized_data = HostNormalizer.normalize_host_data(raw_host)

    assert normalized_data['hostname'] == 'server1'
    assert normalized_data['ip_addresses'] == ['192.168.1.1']
    assert normalized_data['mac_addresses'] == ['00:11:22:33:44:55']