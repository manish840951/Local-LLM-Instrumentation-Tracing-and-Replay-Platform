from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer

MODEL_NAME = "gpt2"

def load_model():

    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    print("Loading model...")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        attn_implementation="eager"
    )

    print("Model loaded successfully!")

    return model, tokenizer