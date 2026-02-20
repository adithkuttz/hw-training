

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "reelly"

API_BASE_URL = "https://api-reelly.up.railway.app/api/internal"

REQUEST_TIMEOUT = 60
RETRY_MAX_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 2

MANUAL_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://find.reelly.io',
    'priority': 'u=1, i',
    'referer': 'https://find.reelly.io/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'xano-authorization': 'eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.2HamAKra83YelGmqJBZalcE8ipNf7MQITTXebZmHet1DyiynRNG5dUDs2A0-xdvqY3pgvowRfrUisqUFKkA2Gmw-Kz8ViNsL.zUFiGnWLyzrNLVBetj5vSg.n6W3DFX1r6jOur-4VlSagSOE0a7p5kzFAeJXjaQRUFZU50w5-W4lLxD2Emp7cueK_r1sftTr9nQ1qxG46yebxSDskqpMFNV-Am3PlfnMY6BvqykizolHXohGPiF0drItKq9rZKbotUuS_nCikR6qhA.z0hUGgm_cCCaaga2lx5gz8bxqZLUeHmWnHsj6suNSPM',
}
