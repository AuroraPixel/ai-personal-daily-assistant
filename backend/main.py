from dotenv import load_dotenv
load_dotenv()

from remote_api.jsonplaceholder.client import JSONPlaceholderClient

client = JSONPlaceholderClient()

print(client.get_users())