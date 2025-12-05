
# # def decorator(func):
# #     def wrapper():
# #         print("printing before the function.")
# #         func()
# #         print("printing after the function.")

# #     return wrapper




# # # def say_hello():
# # #     print("Hello from draft.py!") 

# # # say_hello = decorator(say_hello)

# # # say_hello()


# # @decorator
# # def say_hello():
# #     print("Hello from Zaki!")

# # say_hello()


# myVar = "zaki"

# result = isinstance(myVar, list)
# print(result)

#////////////////////////////////////////

import httpx

def safe_get(url: str, params=None):
    try:
        response = httpx.get(url, params=params)
        response.raise_for_status()        # ← triggers HTTPStatusError on 4xx/5xx
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"HTTP Error": f"HTTP {e.response.status_code} – {e.response.text[:100]}"}
    except httpx.RequestError as e:
        return {"error": f"Network/Request problem: {e}"}
    except Exception as e:
        return {"error": f"Something unexpected: {str(e)}"}

# # 1. Good request → returns real data
# print(safe_get("https://jsonplaceholder.typicode.com/posts/1"))
# # → {'id': 1, 'title': '...', ...}

# # 2. 404 Not Found → triggers HTTPStatusError
# print(safe_get("https://jsonplaceholder.typicode.com/posts/999999"))
# # → {'HTTP Error': 'HTTP 404 – {"message":"..."}'}

# # 3. Invalid domain → triggers RequestError
# print(safe_get("https://this-domain-does-not-exist-12345.com"))
# # → {'error': 'Network/Request problem: [Errno 8] nodename nor servname provided...'}

# 4. Timeout (force a timeout)
print(safe_get("https://jsonplaceholder.typicode.com/posts"))
# → {'error': 'Network/Request problem: timed out'}