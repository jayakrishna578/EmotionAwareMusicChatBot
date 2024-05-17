from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os

app = FastAPI()

# Load your Hugging Face model and tokenizer
model_name = "jayakrishna578/llama-2-7b-health"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Load emotion detection model
emotion_model_name = "jayakrishna578/llama-2-7b-health"
emotion_pipeline = pipeline("text-classification", model=emotion_model_name)

class UserInput(BaseModel):
    prompt: str
    conversation: List[str]

class EmotionInput(BaseModel):
    conversation: List[str]

@app.post("/answer")
async def answer_question(input: UserInput):
    prompt = input.prompt
    conversation = input.conversation
    
    # Format the conversation for the model
    formatted_conversation = "\n".join([f"User: {msg}" if i % 2 == 0 else f"Assistant: {msg}" for i, msg in enumerate(conversation)])
    prompt_text = f"{formatted_conversation}\nUser: {prompt}\nAssistant:"
    
    inputs = tokenizer(prompt_text, return_tensors="pt")
    outputs = model.generate(**inputs)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return {"response": response}

@app.post("/detect_emotion")
async def detect_emotion(input: EmotionInput):
    conversation = input.conversation
    
    # Combine the conversation into a single string
    combined_conversation = " ".join(conversation)
    emotions = emotion_pipeline(combined_conversation)
    
    # Extract the most common emotion
    detected_emotion = emotions[0]["label"]
    
    return {"emotion": detected_emotion}
