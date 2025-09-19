import redis
import os
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), decode_responses=True)
keys = r.keys('embedding:*')
print(keys)