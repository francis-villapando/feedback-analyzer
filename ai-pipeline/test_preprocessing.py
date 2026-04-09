"""Quick test for preprocessing module"""

import sys
import io

# Fix for Windows emoji printing
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.preprocessing import preprocess, preprocess_for_model

# Test with sample messages
test_messages = [
    'Hello Woooorld!',
    "oh no, I don't understand po yung example tbh",
    'THANK YOU PO!!!',
    'Can you explain more clearly?',
    'mas mabilis pa yung sa example',
    'http://example.com is a great resource 😀🤣😌',
    'u r so good n smart, thx!',
]

print('=' * 60)
print('Preprocessing Test Results')
print('=' * 60)

for msg in test_messages:
    result = preprocess(msg)
    print(f'Original: {msg}')
    print(f'Cleaned:  {result["cleaned_text"]}')
    print(f'Tokens:   {result["tokens"]}')
    print('-' * 60)

print("\nAll tests completed successfully!")
