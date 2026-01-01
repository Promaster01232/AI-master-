#!/usr/bin/env python3
import os
import sys
import yaml
import logging
from pathlib import Path
from datetime import datetime
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ModelTrainer:
    """Trainer for fine-tuning models"""
    
    def __init__(self, config_path: str = "./training/training_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
    def load_config(self) -> dict:
        """Load training configuration"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_model(self):
        """Setup model and tokenizer"""
        logger.info(f"Loading base model: {self.config['training']['base_model']}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config['training']['base_model'],
            trust_remote_code=True
        )
        
        # Set padding token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        model_kwargs = {}
        
        # Apply quantization if enabled
        if self.config['training']['quantization']['enabled']:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            model_kwargs['quantization_config'] = quantization_config
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config['training']['base_model'],
            trust_remote_code=True,
            **model_kwargs
        )
        
        # Apply LoRA if enabled
        if self.config['training']['lora']['enabled']:
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.config['training']['lora']['r'],
                lora_alpha=self.config['training']['lora']['alpha'],
                lora_dropout=self.config['training']['lora']['dropout'],
                target_modules=self.config['training']['lora']['target_modules'],
                bias="none",
            )
            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()
        
        logger.info("Model setup complete")
    
    def load_dataset(self, dataset_path: str):
        """Load and prepare dataset"""
        logger.info(f"Loading dataset from {dataset_path}")
        
        # Load dataset based on format
        if dataset_path.endswith('.json'):
            dataset = load_dataset('json', data_files=dataset_path)
        elif dataset_path.endswith('.csv'):
            dataset = load_dataset('csv', data_files=dataset_path)
        else:
            dataset = load_dataset(dataset_path)
        
        # Preprocess function
        def preprocess_function(examples):
            # Format based on dataset format
            format_type = self.config.get('dataset_format', 'conversation')
            
            if format_type == 'conversation':
                texts = []
                for conv in examples['conversation']:
                    text = ""
                    for msg in conv:
                        text += f"{msg['role']}: {msg['content']}\n"
                    texts.append(text)
            elif format_type == 'instruction':
                texts = []
                for inst, resp in zip(examples['instruction'], examples['response']):
                    texts.append(f"Instruction: {inst}\nResponse: {resp}")
            else:
                texts = examples['text']
            
            # Tokenize
            return self.tokenizer(
                texts,
                truncation=True,
                padding="max_length",
                max_length=512
            )
        
        # Tokenize dataset
        tokenized_dataset = dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=dataset["train"].column_names
        )
        
        # Split dataset
        train_test_split = tokenized_dataset["train"].train_test_split(
            test_size=self.config['training']['dataset']['test_split'],
            seed=self.config['training']['dataset']['seed']
        )
        
        train_val_split = train_test_split["train"].train_test_split(
            test_size=self.config['training']['dataset']['val_split'] / 
                     (1 - self.config['training']['dataset']['test_split']),
            seed=self.config['training']['dataset']['seed']
        )
        
        return {
            'train': train_val_split['train'],
            'validation': train_val_split['test'],
            'test': train_test_split['test']
        }
    
    def train(self, dataset_path: str, output_dir: str = None):
        """Train the model"""
        # Setup
        self.setup_model()
        
        # Load dataset
        datasets = self.load_dataset(dataset_path)
        
        # Create output directory
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"./training/output/{timestamp}"
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config['training']['parameters']['epochs'],
            per_device_train_batch_size=self.config['training']['parameters']['batch_size'],
            per_device_eval_batch_size=self.config['training']['evaluation']['per_device_eval_batch_size'],
            gradient_accumulation_steps=self.config['training']['parameters']['gradient_accumulation_steps'],
            warmup_steps=self.config['training']['parameters']['warmup_steps'],
            weight_decay=self.config['training']['parameters']['weight_decay'],
            learning_rate=self.config['training']['parameters']['learning_rate'],
            logging_dir=self.config['training']['logging']['logging_dir'],
            logging_steps=self.config['training']['logging']['steps'],
            eval_strategy=self.config['training']['evaluation']['eval_strategy'],
            save_strategy=self.config['training']['checkpoint']['save_strategy'],
            save_steps=self.config['training']['checkpoint']['save_steps'],
            save_total_limit=self.config['training']['checkpoint']['save_total_limit'],
            load_best_model_at_end=self.config['training']['checkpoint']['load_best_model_at_end'],
            metric_for_best_model=self.config['training']['checkpoint']['metric_for_best_model'],
            fp16=self.config['training']['hardware']['fp16'],
            bf16=self.config['training']['hardware']['bf16'],
            gradient_checkpointing=self.config['training']['hardware']['gradient_checkpointing'],
            report_to=self.config['training']['logging']['report_to'],
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Create trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=datasets['train'],
            eval_dataset=datasets['validation'],
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Start training
        logger.info("Starting training...")
        self.trainer.train()
        
        # Save model
        self.trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save config
        config_save_path = Path(output_dir) / "training_config.yaml"
        with open(config_save_path, 'w') as f:
            yaml.dump(self.config, f)
        
        logger.info(f"Training complete! Model saved to {output_dir}")
        
        return output_dir
    
    def evaluate(self, test_dataset):
        """Evaluate the model"""
        if self.trainer is None:
            raise ValueError("Trainer not initialized. Call train() first.")
        
        logger.info("Evaluating model...")
        results = self.trainer.evaluate(test_dataset)
        
        logger.info(f"Evaluation results: {results}")
        return results

def main():
    """Main training script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train a language model")
    parser.add_argument("--dataset", required=True, help="Path to training dataset")
    parser.add_argument("--config", default="./training/training_config.yaml", help="Training config file")
    parser.add_argument("--output", help="Output directory")
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = ModelTrainer(args.config)
    
    # Train model
    output_dir = trainer.train(args.dataset, args.output)
    
    logger.info(f"✅ Training complete! Model saved to: {output_dir}")

if __name__ == "__main__":
    main()