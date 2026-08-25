from langchain_ollama import OllamaLLM


llm = OllamaLLM(model="qwen2.5:7b-instruct")


while True:
    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    print("\nQwen: ", end="", flush=True)

    for chunk in llm.stream(user_input):
        print(chunk, end="", flush=True)

    print()