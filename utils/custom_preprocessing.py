from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
import torch
from config import (
    NUM_BEAMS,
    NO_REPEAT_NGRAM_SIZE,
    MAX_LENGTH,
)

def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    tokenizer.padding_side = "left"

    config = AutoConfig.from_pretrained(model_name)

    if "rope_scaling" not in config:
        config.rope_scaling = {
            'type': 'llama3',
            'factor': 8.0,
            'low_freq_factor': 1.0,
            'high_freq_factor': 4.0,
            'original_max_position_embeddings': 8192
        }

    if tokenizer.eos_token_id is None:
        tokenizer.eos_token_id = tokenizer.convert_tokens_to_ids("</s>")

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        config=config,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    return model, tokenizer

def chat(input_message, model_name):
    model, tokenizer = load_model(model_name)

    messages = [
        {"role": "system", "content": "You are a math teacher"},
        {"role": "user", "content": input_message},
    ]

    inputs = tokenizer(
        [message["content"] for message in messages],
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH
    ).to(model.device)

    if "input_ids" not in inputs:
        raise ValueError("No input_ids found in tokenizer output.")

    input_ids = inputs["input_ids"]

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    if terminators[0] is None:
        raise ValueError("eos_token_id is None, please check the tokenizer.")

    outputs = model.generate(
        input_ids,
        max_new_tokens=256,
        eos_token_id=terminators[0], 
        pad_token_id=tokenizer.pad_token_id,
        attention_mask=inputs["attention_mask"],
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        num_return_sequences=1,
        top_k=50,
        no_repeat_ngram_size=3,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(response)

    return {"response": response}

def clean_response(response, prompt):
    """
    Clean responses generated by LLM
    """
    cleaned_response = response.replace(prompt, "").strip()

    return cleaned_response