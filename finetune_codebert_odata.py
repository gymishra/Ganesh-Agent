#!/usr/bin/env python3
"""
Fine-tune CodeBERT with OData MCP knowledge
"""

import json
import torch
from transformers import (
    RobertaTokenizer, 
    RobertaForSequenceClassification,
    RobertaConfig,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)
from torch.utils.data import Dataset
import numpy as np
from typing import List, Dict, Any

class ODataCodeDataset(Dataset):
    """Dataset for OData code generation training"""
    
    def __init__(self, examples: List[Dict[str, str]], tokenizer, max_length=512):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        example = self.examples[idx]
        
        # Combine natural language and code for training
        input_text = f"Natural Language: {example['natural_language']} Code: {example['code']}"
        
        # Tokenize
        encoding = self.tokenizer(
            input_text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()  # For language modeling
        }

class CodeBERTODataFineTuner:
    def __init__(self, model_name="microsoft/codebert-base"):
        self.model_name = model_name
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.model = None
        
    def load_training_data(self, data_file: str) -> List[Dict[str, str]]:
        """Load training data from JSON file"""
        with open(data_file, 'r') as f:
            data = json.load(f)
        return data.get('examples', [])
    
    def prepare_model(self, num_labels=2):
        """Prepare CodeBERT model for fine-tuning"""
        config = RobertaConfig.from_pretrained(
            self.model_name,
            num_labels=num_labels
        )
        
        self.model = RobertaForSequenceClassification.from_pretrained(
            self.model_name,
            config=config
        )
        
        # Add special tokens for OData
        special_tokens = [
            "<ODATA_FILTER>", "<ODATA_SELECT>", "<ODATA_EXPAND>", 
            "<ODATA_ORDERBY>", "<ENTITY_SET>", "<FUNCTION_IMPORT>"
        ]
        
        self.tokenizer.add_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def create_training_examples(self, examples: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Enhance examples with OData-specific patterns"""
        enhanced_examples = []
        
        for example in examples:
            # Original example
            enhanced_examples.append(example)
            
            # Add variations with special tokens
            if '$filter' in example['code']:
                enhanced_example = example.copy()
                enhanced_example['code'] = enhanced_example['code'].replace(
                    '$filter', '<ODATA_FILTER>'
                )
                enhanced_examples.append(enhanced_example)
            
            # Add entity set tagging
            if any(op in example['code'] for op in ['filter_', 'get_', 'create_', 'update_']):
                enhanced_example = example.copy()
                for op in ['filter_', 'get_', 'create_', 'update_']:
                    if op in enhanced_example['code']:
                        entity = enhanced_example['code'].split(op)[1].split('(')[0]
                        enhanced_example['code'] = enhanced_example['code'].replace(
                            f"{op}{entity}", f"{op}<ENTITY_SET>{entity}</ENTITY_SET>"
                        )
                enhanced_examples.append(enhanced_example)
        
        return enhanced_examples
    
    def fine_tune(self, training_data_file: str, output_dir: str = "/home/gyanmis/codebert_odata_model"):
        """Fine-tune CodeBERT on OData examples"""
        
        # Load and prepare data
        examples = self.load_training_data(training_data_file)
        enhanced_examples = self.create_training_examples(examples)
        
        print(f"Training on {len(enhanced_examples)} examples")
        
        # Prepare model
        self.prepare_model()
        
        # Create dataset
        dataset = ODataCodeDataset(enhanced_examples, self.tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="steps",
            eval_steps=500,
            save_total_limit=2,
            load_best_model_at_end=True,
        )
        
        # Data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            eval_dataset=dataset,  # Using same dataset for simplicity
            data_collator=data_collator,
        )
        
        # Train
        print("Starting fine-tuning...")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"Model saved to {output_dir}")
    
    def generate_odata_code(self, natural_language: str, max_length=100):
        """Generate OData code from natural language"""
        if not self.model:
            raise ValueError("Model not loaded. Call fine_tune() first or load a pre-trained model.")
        
        input_text = f"Natural Language: {natural_language} Code:"
        
        inputs = self.tokenizer(
            input_text,
            return_tensors='pt',
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the code part
        if "Code:" in generated_text:
            code = generated_text.split("Code:")[-1].strip()
            return code
        
        return generated_text

def main():
    # Initialize fine-tuner
    fine_tuner = CodeBERTODataFineTuner()
    
    # Fine-tune on OData examples
    training_data_file = "/home/gyanmis/codebert_odata_training_data.json"
    
    if not os.path.exists(training_data_file):
        print(f"Training data file not found: {training_data_file}")
        print("Please run extract_mcp_training_data.py first")
        return
    
    try:
        fine_tuner.fine_tune(training_data_file)
        
        # Test the fine-tuned model
        print("\nTesting fine-tuned model:")
        test_queries = [
            "Get all products with price greater than 50",
            "Create a new customer",
            "Filter orders by date range",
            "Update product information"
        ]
        
        for query in test_queries:
            try:
                code = fine_tuner.generate_odata_code(query)
                print(f"Query: {query}")
                print(f"Generated Code: {code}")
                print("-" * 50)
            except Exception as e:
                print(f"Error generating code for '{query}': {e}")
    
    except Exception as e:
        print(f"Error during fine-tuning: {e}")

if __name__ == "__main__":
    import os
    main()
