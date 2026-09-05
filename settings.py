import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def get_parameter(name):
    env_value = os.getenv(name)
    if env_value:
        return env_value

    ssm = boto3.client('ssm', region_name=os.getenv('AWS_REGION', 'us-east-2'))
    return ssm.get_parameter(
        Name=f"/rollplay-scion/{name}",
        WithDecryption=True
    )['Parameter']['Value']


def get_optional_parameter(name, default=None):
    try:
        return get_parameter(name)
    except Exception:
        return default

# Fetch Environment
ENVIRONMENT = get_optional_parameter("ENVIRONMENT", default="prod")


# -----------------------------
# TOKEN SWITCHING LOGIC
# -----------------------------
if ENVIRONMENT == "dev":
    SECRET_KEY = get_optional_parameter("TESTING_BOT_TOKEN")
else:
    SECRET_KEY = get_optional_parameter("SECRET_KEY")

# Fetch test server ID
TESTING_SERVER = get_optional_parameter('TESTING_SERVER', default=os.getenv('TESTING_SERVER'))

# Optional channel ID for reactive defense debug logs.
# Falls back to the testing channel if the SSM parameter is not set.
REACTIVE_DEFENSE_LOG_CHANNEL = get_optional_parameter(
    'REACTIVE_DEFENSE_LOG_CHANNEL',
    default=os.getenv('REACTIVE_DEFENSE_LOG_CHANNEL', '1001211424615448607')
)

