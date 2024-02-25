import unittest
from main import TCPclient

class TestTCPClient(unittest.TestCase):
    """
    Unit tests for the TCPClient class.
    """

    def test_hello_message(self):
        ipv4 = "127.0.0.1"
        port = 8080
        peerid = "abc123"
        messages = []
        response = TCPclient(ipv4, port, peerid, messages)
        self.assertEqual(response["command"], "hello")
        self.assertEqual(response["peer_id"], peerid)

    def test_send_messages(self):
        ipv4 = "127.0.0.1"
        port = 8080
        peerid = "abc123"
        messages = [
            {"message_id": 1, "message": "Hello"},
            {"message_id": 2, "message": "World"}
        ]
        response = TCPclient(ipv4, port, peerid, messages)
        self.assertEqual(response["command"], "new_message")
        self.assertEqual(response["message_id"], messages[-1]["message_id"])
        self.assertEqual(response["message"], messages[-1]["message"])

if __name__ == "__main__":
    unittest.main()