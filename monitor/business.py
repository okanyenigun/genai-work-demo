
import json
import random


class DomainTwo:

    async def do(self, i):  # Make it async and accept a parameter
        value = random.randint(0, 100)
        return json.dumps({'data': i})
