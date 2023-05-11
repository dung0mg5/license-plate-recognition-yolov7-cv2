import re
def get_valid_chars(input_str):
    valid_chars = []
    for char in input_str:
        if char.isalnum() or char in ['-', '.']:
            valid_chars.append(char)
    return ''.join(valid_chars)


plate_pattern = r'^[0-9]{2}[A-Z]{1}-?[0-9]{3}\.?[0-9]{2}$'

def is_valid_license_plate(plate):
    return bool(re.match(plate_pattern, plate))