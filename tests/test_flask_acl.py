import unittest
from unittest.mock import patch, MagicMock
import json
import psycopg2
from flask import Flask
from main import ConfigHandler, DatabaseHandler, APIHandler, app 

class TestConfigHandler(unittest.TestCase):
    """Test ConfigHandler"""
    
    @patch("builtins.open", unittest.mock.mock_open(read_data="mappings: []"))
    @patch("os.getenv", side_effect=lambda key, default=None: default if "CONFIG_YAML_PATH" else "test.yaml")
    def test_load_config(self, mock_getenv):
        """Test load_config to read YAML"""
        config = ConfigHandler()
        self.assertEqual(config.mappings, []) 

    @patch("os.getenv", side_effect=lambda key, default=None: {"DB_USER": "test_user", "DB_HOST": "localhost"}.get(key, default))
    def test_load_db_config(self, mock_getenv):
        """Test load_db_config load env"""
        config = ConfigHandler()
        self.assertEqual(config.db_config["user"], "test_user")
        self.assertEqual(config.db_config["host"], "localhost")


class TestDatabaseHandler(unittest.TestCase):
    """Test DatabaseHandler"""

    @patch("psycopg2.connect")
    def test_execute_query(self, mock_connect):
        """Test execute_query() and return"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Alice", 25), ("Bob", 30)]
        mock_cursor.description = [("name",), ("age",)]

        config = ConfigHandler()
        db = DatabaseHandler(config)
        result, columns = db.execute_query("SELECT * FROM users")

        self.assertEqual(result, [("Alice", 25), ("Bob", 30)])
        self.assertEqual(columns, ["name", "age"])


class TestAPIHandler(unittest.TestCase):
    """Test APIHandler"""
    
    @patch("psycopg2.connect")
    def setUp(self, mock_connect):
        """Init Flask testing client"""
        self.app = app.test_client()
        self.config_handler = ConfigHandler()
        self.db_handler = DatabaseHandler(self.config_handler)
        self.api_handler = APIHandler(self.config_handler, self.db_handler)

    @patch("psycopg2.connect")
    def test_health_check(self, mock_connect):
        """Test /health API"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.app.get("/health")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["db_connection"], "ok")

    @patch("psycopg2.connect")
    def test_valid_api_endpoint(self, mock_connect):
        """Test /users API"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Alice", "xxx@abc.com"), ("Bob", "bbb@abc.com")]
        mock_cursor.description = [("name",), ("email",)]

        response = self.app.get("/users")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [{"user_name": "Alice", "user_email": "xxx@abc.com"}, {"user_name": "Bob", "user_email": "bbb@abc.com"}])

    def test_invalid_api_endpoint(self):
        """Test invalid API adn return 404"""
        response = self.app.get("/invalid_endpoint")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Invalid API Endpoint")


if __name__ == "__main__":
    unittest.main()
