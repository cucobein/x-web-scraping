#!/usr/bin/env python3
"""
Debug script to explore Firebase Remote Config response structure
"""

import asyncio
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, remote_config

# Load .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

async def debug_firebase_config():
    """Debug Firebase Remote Config response"""
    
    # Load .env file
    load_env_file()
    
    # Initialize Firebase
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    
    if not project_id or not service_account_path:
        print("❌ Missing Firebase environment variables")
        print(f"  FIREBASE_PROJECT_ID: {project_id}")
        print(f"  FIREBASE_SERVICE_ACCOUNT_PATH: {service_account_path}")
        return
    
    try:
        # Initialize Firebase app
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {"projectId": project_id})
        
        print("✅ Firebase initialized")
        
        # Get server template
        print("🔄 Getting server template...")
        template = await remote_config.get_server_template()
        print(f"✅ Template type: {type(template)}")
        print(f"✅ Template dir: {dir(template)}")
        
        # Evaluate template
        print("🔄 Evaluating template...")
        server_config = template.evaluate()
        print(f"✅ ServerConfig type: {type(server_config)}")
        print(f"✅ ServerConfig dir: {dir(server_config)}")
        
        # Try to access attributes
        print("\n🔍 Exploring ServerConfig attributes:")
        for attr in dir(server_config):
            if not attr.startswith('_'):
                try:
                    value = getattr(server_config, attr)
                    print(f"  {attr}: {type(value)} = {value}")
                except Exception as e:
                    print(f"  {attr}: Error accessing - {e}")
        
        # Try to convert to dict
        print("\n🔍 Trying to convert to dict:")
        try:
            config_dict = server_config.__dict__
            print(f"  __dict__: {config_dict}")
            
            # Explore _config_values
            if '_config_values' in config_dict:
                print("\n🔍 Exploring _config_values:")
                config_values = config_dict['_config_values']
                print(f"  Type: {type(config_values)}")
                print(f"  Keys: {list(config_values.keys())}")
                
                # Try to get a sample value
                for key, value in config_values.items():
                    print(f"  {key}: {type(value)} = {value}")
                    # Try to access the value's attributes
                    if hasattr(value, '__dict__'):
                        print(f"    __dict__: {value.__dict__}")
                    if hasattr(value, 'value'):
                        print(f"    .value: {value.value}")
                    break  # Just show first one
                    
        except Exception as e:
            print(f"  __dict__ error: {e}")
        
        # Try JSON conversion
        print("\n🔍 Trying JSON conversion:")
        try:
            import json
            config_json = json.dumps(server_config, default=str)
            print(f"  JSON: {config_json}")
        except Exception as e:
            print(f"  JSON error: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_firebase_config()) 