#!/usr/bin/env python3
import os
import json
import subprocess
import sys
from pathlib import Path

MODELS_CONFIG = {
    "qwen2.5:7b": {
        "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_K_M.gguf",
        "filename": "qwen2.5-7b-instruct-q4_K_M.gguf",
        "size": "4.5GB"
    },
    "llama3.2:3b": {
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "filename": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "size": "2GB"
    },
    "mistral:7b": {
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "size": "4.5GB"
    }
}

def download_model(model_name, model_info):
    """Download a model using curl"""
    print(f"\n📥 Downloading {model_name}...")
    print(f"Size: {model_info['size']}")
    
    # Create directory
    model_type = model_name.split(":")[0]
    model_dir = Path(f"./ai-models/{model_type}")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = model_dir / model_info['filename']
    
    if filepath.exists():
        print(f"✓ Model already exists at {filepath}")
        return True
    
    try:
        # Download using curl with progress bar
        cmd = [
            "curl", "-L", model_info['url'],
            "-o", str(filepath),
            "--progress-bar"
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                print(output.decode().strip(), end='\r')
        
        if process.returncode == 0:
            print(f"\n✓ Downloaded {model_name} successfully!")
            return True
        else:
            print(f"\n✗ Failed to download {model_name}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def setup_ollama():
    """Set up Ollama if not installed"""
    print("\n🔧 Setting up Ollama...")
    
    # Check if Ollama is installed
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        print("✓ Ollama is already installed")
    except:
        print("Ollama not found. Installing...")
        # Download and install Ollama
        subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"])
    
    # Pull models
    print("\n🔄 Pulling models from Ollama...")
    models = ["qwen2.5:7b", "llama3.2:3b", "mistral:7b", "nomic-embed-text"]
    
    for model in models:
        print(f"Pulling {model}...")
        subprocess.run(["ollama", "pull", model])

def main():
    print("🤖 AI Model Setup Script")
    print("=" * 50)
    
    # Create directories
    Path("./ai-models").mkdir(exist_ok=True)
    Path("./ai-models/llama").mkdir(exist_ok=True)
    Path("./ai-models/qwen").mkdir(exist_ok=True)
    Path("./ai-models/mistral").mkdir(exist_ok=True)
    Path("./ai-models/embeddings").mkdir(exist_ok=True)
    Path("./ai-models/finetuned").mkdir(exist_ok=True)
    
    # Setup Ollama
    setup_ollama()
    
    # Save config
    config_path = Path("./ai-models/models.json")
    with open(config_path, 'w') as f:
        json.dump(MODELS_CONFIG, f, indent=2)
    
    print("\n✅ Model setup complete!")
    print("\nNext steps:")
    print("1. Run: ollama serve")
    print("2. Run: npm run dev")
    print("3. Open: http://localhost:3000")

if __name__ == "__main__":
    main()