import os
os.environ["HTTPX_DISABLE_HTTP2"] = "1"
import httpx
import time
# from supabase.lib.client_options import ClientOptions
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path



# Disable HTTP/2 globally via environment variable


from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)



SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase environment variables not loaded")



supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def safe_execute(table_call, retries=3, delay=1):
    for _ in range(retries):
        try:
            return table_call.execute().data
        except Exception as e:
            print("Supabase call failed, retrying...", e)
            time.sleep(delay)
    raise RuntimeError("Supabase call failed after retries")



# # 🔥 Create a custom HTTP client (THIS FIXES YOUR ERROR)
# http_client = httpx.Client(
#     http2=False,  # Disable HTTP/2 (fixes RemoteProtocolError)
#     limits=httpx.Limits(
#         max_keepalive_connections=0,  # Avoid reusing dead connections
#         max_connections=10
#     ),
#     timeout=30.0
# )

# options = ClientOptions(http_client=http_client)




# supabase = create_client(SUPABASE_URL, SUPABASE_KEY,http_client=http_client)
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY,options=options)