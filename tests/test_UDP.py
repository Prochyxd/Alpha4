import unittest
from main import UDPdiscovery

class TestUDPDiscovery(unittest.TestCase):
    """
    Test case class for UDP discovery functionality.
    """

    def test_udp_discovery(self):
        # Test case 1: Valid IPv4 address and port
        ipv4 = "192.168.0.1"
        port = 1234
        mask = None
        peerid = "abc123"
        expected_response = {"status": "ok", "peer_id": "abc123"}
        self.assertEqual(UDPdiscovery(ipv4, port, mask, peerid), expected_response)

        # Test case 2: Invalid IPv4 address
        ipv4 = "invalid_ip"
        port = 1234
        mask = None
        peerid = "abc123"
        expected_response = {"status": "error", "message": "Invalid IPv4 address"}
        self.assertEqual(UDPdiscovery(ipv4, port, mask, peerid), expected_response)

        # Test case 3: Invalid port number
        ipv4 = "192.168.0.1"
        port = -1
        mask = None
        peerid = "abc123"
        expected_response = {"status": "error", "message": "Invalid port number"}
        self.assertEqual(UDPdiscovery(ipv4, port, mask, peerid), expected_response)

        # Test case 4: Timeout
        ipv4 = "192.168.0.1"
        port = 1234
        mask = None
        peerid = "abc123"
        expected_response = {"status": "error", "message": "Timeout"}
        self.assertEqual(UDPdiscovery(ipv4, port, mask, peerid), expected_response)

if __name__ == '__main__':
    unittest.main()