import torch
import os
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer
)
from transformers.utils.quantization_config import BitsAndBytesConfig
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from parrot_ai.prompts import MAIN_SYSTEM_PROMPT

class ParrotAI:
    """A class for loading and using 4-bit quantized causal language models."""
    
    def __init__(self):
        """Initialize ParrotAI instance."""
        self.model = None
        self.tokenizer = None
        self.model_name = None
    
    def load_model(self, model_name: str):
        """Load a 4-bit quantised causal-LM with automatic GPU sharding."""
        # Clear GPU memory
        torch.cuda.empty_cache()
        
        bnb_cfg = BitsAndBytesConfig(
            load_in_4bit=True,          # activate 4-bit weights
            bnb_4bit_quant_type="nf4",  # normal-float-4, best accuracy
            bnb_4bit_compute_dtype=torch.bfloat16,  # use bfloat16 for better numerical stability
            bnb_4bit_use_double_quant=True  # nested quantization for additional memory savings
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_cfg,
            device_map="auto",           # spreads layers CPU↔GPU if needed
            torch_dtype="auto"           # use model's native dtype for non-quantized modules
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Set pad_token if not already set (important for batch generation)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model_name = model_name
        print(f"Model {model_name} loaded successfully!")
    
    def generate(
        self,
        prompt: str,
        system: str | None = MAIN_SYSTEM_PROMPT,
        max_new_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float = 0.9,
    ):
        """
        One-shot text generation, chat-template aware.
        Returns the assistant reply only.
        """
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not loaded. Please call load_model() first.")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        chat = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        inputs = self.tokenizer([chat], return_tensors="pt").to(self.model.device)

        with torch.no_grad():  # Ensure no gradients for inference
            gen_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # strip the prompt tokens so you only get the new text
        reply_ids = gen_ids[0, inputs.input_ids.shape[1]:]
        return self.tokenizer.decode(reply_ids, skip_special_tokens=True)
    
    def is_loaded(self) -> bool:
        """Check if a model is currently loaded."""
        return self.model is not None and self.tokenizer is not None
    
    def get_model_info(self) -> str:
        """Get comprehensive information about the currently loaded model."""
        if not self.is_loaded():
            return "No model loaded"
        
        assert self.model is not None # Ensure model is not None for type checker
        info_lines = [
            f"Model Name: {self.model_name}",
            f"Memory Footprint: {self.model.get_memory_footprint() / 1e9:.2f} GB",
            f"Total Parameters: {self.model.num_parameters():,}",
            f"Trainable Parameters: {self.model.num_parameters(only_trainable=True):,}",
        ]
        
        # Add model configuration information
        config = self.model.config
        if hasattr(config, 'model_type'):
            info_lines.append(f"Model Type: {config.model_type}")
        if hasattr(config, 'hidden_size'):
            info_lines.append(f"Hidden Size: {config.hidden_size}")
        if hasattr(config, 'num_hidden_layers'):
            info_lines.append(f"Number of Layers: {config.num_hidden_layers}")
        if hasattr(config, 'num_attention_heads'):
            info_lines.append(f"Attention Heads: {config.num_attention_heads}")
        if hasattr(config, 'vocab_size'):
            info_lines.append(f"Vocabulary Size: {config.vocab_size:,}")
        if hasattr(config, 'max_position_embeddings'):
            info_lines.append(f"Max Position Embeddings: {config.max_position_embeddings:,}")
        
        # Add device and dtype information
        try:
            device = next(self.model.parameters()).device
            dtype = next(self.model.parameters()).dtype
            info_lines.extend([
                f"Device: {device}",
                f"Data Type: {dtype}",
            ])
        except StopIteration:
            pass
        
        # Add quantization information
        if hasattr(self.model, 'is_quantized') and self.model.is_quantized:
            info_lines.append("Quantization: 4-bit (BitsAndBytes)")
        
        # Add generation capability
        if hasattr(self.model, 'can_generate') and self.model.can_generate():
            info_lines.append("Generation: Supported")
        
        return "\n".join(info_lines)

class ParrotAIHF:
    """A class for using HuggingFace API for text generation."""
    
    def __init__(self, provider: str = "nebius"):
        """Initialize ParrotAIHF instance with HuggingFace API client."""
        # Load environment variables
        load_dotenv()
        
        # Get HF token from environment
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN must be set in environment variables")
        
        self.client = InferenceClient(
            api_key=hf_token,
        )
        self.provider = provider
        self.model_name = None
        print(f"HuggingFace API client initialized")
    
    def set_model(self, model_name: str):
        """Set the model to use for generation."""
        self.model_name = model_name
        print(f"Model set to: {model_name}")
    
    def generate(
        self,
        prompt: str,
        system: str | None = MAIN_SYSTEM_PROMPT,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float = 0.9,
    ):
        """
        Generate text using HuggingFace API.
        Returns the assistant reply only.
        """
        # Use provided model or fallback to instance model or default
        model_to_use = model or self.model_name or "google/gemma-3-27b-it"
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        completion = self.client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        
        return completion.choices[0].message.content
    
    def is_loaded(self) -> bool:
        """Check if the API client is initialized."""
        return self.client is not None
    
    def get_model_info(self) -> str:
        """Get information about the current configuration."""
        if not self.is_loaded():
            return "API client not initialized"
        
        info_lines = [
            f"Provider: {self.provider}",
            f"Current Model: {self.model_name or 'Not set (will use default)'}",
            "Type: HuggingFace API Client",
        ]
        
        return "\n".join(info_lines)