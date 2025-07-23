import requests

API_URL = "http://localhost:8000/query"

print("🧠 E-commerce AI Assistant (CLI)")
print("Type your question below (or 'exit' to quit)\n")

while True:
    question = input("🔍 Your question: ").strip()
    if question.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    try:
        response = requests.post(API_URL, json={"question": question})
        data = response.json()

        print("\n📄 Generated SQL:")
        sql = data.get("answer", {}).get("sql", None)
        print(sql if sql else "Not available")

        print("\n🧠 Answer:")
        print(data.get("answer", {}).get("answer", "No answer returned."))

        print("\n📊 Results:")
        results = data.get("answer", {}).get("results", [])
        if results:
            for row in results:
                print(row)
        else:
            print("No results found.")

        print("\n" + "-" * 50 + "\n")

    except Exception as e:
        print(f"🚨 Error: {e}")
