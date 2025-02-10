import os
import yaml
import psycopg2
import logging
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MessageHandler:
    """
    Handle messages
    """
    db_connection_error = "Database connection failed"
    invalid_api_endpoint = "Invalid API Endpoint"
    invalid_api_config = "Invalid API configuration"
    health_check_error = "Health check error"
    


app = Flask(__name__)

class ConfigHandler:
    """
    Handle configurations
    """
    def __init__(self):
        self.config_path = os.getenv("CONFIG_YAML_PATH", "config.yaml")
        self.mappings = self.load_config()
        self.db_config = self.load_db_config()
        self.metadata = self.load_metadata()
        
    def load_metadata(self):
        """
        Metadata for the service
        """
        return {
            "version": os.getenv("APP_VERSION", "unknown"),
            "is_kubernetes": os.getenv("IS_KUBERNETES", "false")
        }

    def load_config(self):
        """
        Read YAML config
        """
        logging.info(f"Loading config from {self.config_path}")
        try:
            with open(self.config_path, "r") as file:
                data = yaml.safe_load(file)
                return data.get("mappings", [])
        except Exception as e:
            logging.error(f"Error loading {self.config_path}: {e}")
            return []

    def load_db_config(self):
        """
        Read DB config
        """
        return {
            "user": os.getenv("DB_USER", "postgres"),
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "mydb"),
            "password": os.getenv("DB_PASSWORD", "password"),
            "port": int(os.getenv("DB_PORT", 5432)),
        }


class DatabaseHandler:
    """
    Handle database connections and SQL queries
    """
    def __init__(self, config):
        self.config = config.db_config

    def execute_query(self, query):
        """
        Execute SQL query and return results

        TODO: Improve connection managements
        """
        db_config = self.config
        try:
            print(f"Connecting to database: {db_config['database']} on {db_config['host']}:{db_config['port']}")
            conn = psycopg2.connect(**db_config)
        except Exception as e:
            print (f"Database connection error: {e}")
            conn = None
    
        try:
            cur = conn.cursor()
            cur.execute(query)
            data = cur.fetchall()

            # decsciption is a tuple of column names, column types, etc.
            db_columns = [description[0] for description in cur.description]
            cur.close()

            return data, db_columns
        
        except Exception as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()


class APIHandler:
    """
    Handle API endpoints and requests
    """
    def __init__(self, config_handler, db_handler):
        self.config_handler = config_handler
        self.db_handler = db_handler

    def get_query_config(self, path):
        """
        Retrieve query configuration for API path
        """
        normalized_path = f"/{path}" if not path.startswith("/") else path
        for mapping in self.config_handler.mappings:
            if mapping['api_endpoint'] == normalized_path:
                return mapping
        return None

    def transform_data(self, data, db_columns, columns):
        """
        Transform database query results to API JSON format
        """
        transformed = []
        
        for row in data:
            transformed_row = {}
            
            for db_column, api_field in columns.items():

                # in case the query result doesn't contain all columns
                if db_column in db_columns:  
                    col_idx = db_columns.index(db_column)
                    transformed_row[api_field] = row[col_idx]
            
            transformed.append(transformed_row)
        return transformed

    def handle_request(self, path):
        """
        Handle API request
        """
        query_config = self.get_query_config(path)

        if not query_config:
            return jsonify({'error': f'{message_handler.invalid_api_endpoint}'}), 404

        query = query_config.get('query')
        columns = query_config.get('columns')

        if not query or not columns:
            return jsonify({'error': f'{message_handler.invalid_api_config}'}), 400

        data, db_columns = self.db_handler.execute_query(query)

        if data is None:
            return jsonify({'error': db_columns}), 500

        transformed_data = self.transform_data(data, db_columns, columns)
        logging.info(f'Query Result: {transformed_data}')
        return jsonify(transformed_data)

    def health_check(self):
        """
        Health check API, return service status and database connection status
        """
        result = ""
        try:
            result, _ = db_handler.execute_query("SELECT 1")
            status = "ok" if result else "error"
            message = ""
            db_status = "ok" if result else "failed"
            status_code = 200 if result else 500
        except Exception as e:
            logging.error(f"{message_handler.health_check_error}: {e}")
            status = "error"
            message = str(e)
            db_status = "failed"
            status_code = 500

        return jsonify({
            "status": status,
            "message": message,
            "db_connection": db_status,
            "version": self.config_handler.metadata["version"],
            "is_kubernetes": self.config_handler.metadata["is_kubernetes"]
        }), status_code


message_handler = MessageHandler()
config_handler = ConfigHandler()
db_handler = DatabaseHandler(config_handler)
api_handler = APIHandler(config_handler, db_handler)

@app.route("/<path:path>")
def dynamic_route(path):
    return api_handler.handle_request(path)

@app.route("/health")
def health_check():
    return api_handler.health_check()

