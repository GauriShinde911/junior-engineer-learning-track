# custom exception for validation failures
class ValidationError(Exception):
    pass

# checks if an email string has a basic valid structure
def validate_email(email):
    if not isinstance(email, str):
        raise ValidationError("Email must be a string")
    cleaned = email.strip()
    if "@" not in cleaned or "." not in cleaned or " " in cleaned:
        raise ValidationError(f"Invalid email address: '{email}'")
    parts = cleaned.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValidationError(f"Invalid email structure: '{email}'")
    return cleaned

# checks if a numeric value is strictly greater than zero
def validate_positive_number(value):
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Expected a number, got '{value}'")
    if num <= 0:
        raise ValidationError(f"Number must be greater than zero, got {num}")
    return num

# checks if a text string is not empty or just whitespace
def validate_non_empty(text):
    if not isinstance(text, str) or not text.strip():
        raise ValidationError("Text field cannot be empty")
    return text.strip()

if __name__ == "__main__":
    print("--- Demonstrating Validators ---\n")
    
    # 1. Email validation demo
    print("Testing Email Validator:")
    try:
        print("Valid email:  ", validate_email("user@example.com"))
    except ValidationError as e:
        print("Error:", e)
        
    try:
        validate_email("bad-email-without-at.com")
    except ValidationError as e:
        print("Invalid email:", e)
        
    # 2. Positive number validation demo
    print("\nTesting Positive Number Validator:")
    try:
        print("Valid number:  ", validate_positive_number("42.5"))
    except ValidationError as e:
        print("Error:", e)
        
    try:
        validate_positive_number("-10")
    except ValidationError as e:
        print("Invalid number:", e)
        
    # 3. Non-empty string validation demo
    print("\nTesting Non-Empty Text Validator:")
    try:
        print("Valid text:    ", validate_non_empty("Hello Python!"))
    except ValidationError as e:
        print("Error:", e)
        
    try:
        validate_non_empty("   ")
    except ValidationError as e:
        print("Invalid text:  ", e)
