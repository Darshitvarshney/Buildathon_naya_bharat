from google import genai
client = genai.Client(api_key="AIzaSyB3ZuN2qaxUks0bi4ZSvyYvgDRA6CoqN7U")

for m in client.models.list():
    print(m.name)
