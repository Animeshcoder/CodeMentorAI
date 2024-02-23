import openai

# Set your API key
openai.api_key = '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'

# Define a function to generate a response
def generate_response(prompt):
    try:
        response = openai.Completion.create(
            engine="gpt-4-0125-preview",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)

# Test the function
print(generate_response("Hello, world!"))
