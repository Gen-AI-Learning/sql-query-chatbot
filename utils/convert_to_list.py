import ast

def convert_to_list(data_string):
    # Check if the string is empty
    if not data_string.strip():
        return []
    
    try:
        # Attempt to evaluate the string
        result = ast.literal_eval(data_string)
        # Check if the result is a list
        if isinstance(result, list):
            return result
        else:
            return data_string
    except (ValueError, SyntaxError):
        # Return an empty list if the string is not a valid list
        return data_string