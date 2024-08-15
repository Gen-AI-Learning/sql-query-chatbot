import re

def is_confirmation_request(response):
    patterns = [
        r"would you like (me )?to (run|execute) this query",
        r"(do you want|shall I) (to )?(run|execute) (this|the) query",
        r"(are you sure|confirm) (you want )?to (run|execute) (this|the) query",
        r"(should I|do you wish to) proceed with (running|executing) (this|the) query"
    ]
    return any(re.search(pattern, response.lower()) for pattern in patterns)

def extract_query(response):
    # Try to find SQL query in the response
    sql_match = re.search(r"```sql\n(.*?)\n```", response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    
    # If no SQL block found, try to find the last sentence that looks like a query
    sentences = re.split(r'(?<=[.!?])\s+', response)
    for sentence in reversed(sentences):
        if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', sentence, re.IGNORECASE):
            return sentence.strip()
    
    # If no query-like sentence found, return the entire response
    return response