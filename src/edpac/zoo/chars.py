
import string

# Define the 64-character alphabet
# Standard: A-Z, a-z, 0-9, +, /
CHARS = string.ascii_uppercase.replace('X', '') + string.ascii_lowercase + string.digits + "+/@#"

def index_to_char(index):
    """Convert index 0-63 to a single character."""
    return CHARS[index]

def char_to_index(char):
    """Convert a character back to an index 0-63."""
    # .find() is very fast for a string of length 64
    return CHARS.find(char)

if __name__ == "__main__":

    # --- Verification ---
    print(f"Total Characters: {len(CHARS)}")
    print(f"Contains 'X'? {'X' in CHARS}")
    print(f"Example: Index 0 is '{index_to_char(0)}', Index 64 is '{index_to_char(64)}'")
