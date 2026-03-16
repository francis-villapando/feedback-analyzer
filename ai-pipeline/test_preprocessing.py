"""Quick test for preprocessing module"""

from src.preprocessing import preprocess

# Test with sample messages
test_messages = [
    'Hello World!',
    "I don't understand po yung example",
    'THANK YOU PO!',
    'Can you explain more clearly?',
    'mas mabilis pa yung sa example'
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
