import os
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, PeftModel
from trl import SFTTrainer

class LlamaFineTuner:
    def __init__(self, model_name, dataset_name, new_model_name, output_dir, **kwargs):
        # Initialize class variables with default and keyword arguments
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.new_model_name = new_model_name
        self.output_dir = output_dir
        self.configurations = kwargs

    def load_dataset(self):
        """Load the dataset for training."""
        return load_dataset(self.dataset_name, split="train")

    def prepare_quantization_config(self):
        """Prepare the quantization configuration based on provided settings."""
        compute_dtype = getattr(torch, self.configurations['bnb_4bit_compute_dtype'])
        return BitsAndBytesConfig(
            load_in_4bit=self.configurations['use_4bit'],
            bnb_4bit_quant_type=self.configurations['bnb_4bit_quant_type'],
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=self.configurations['use_nested_quant'],
        )

    def load_model_and_tokenizer(self, quantization_config):
        """Load the model and tokenizer with the specified configurations."""
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name, quantization_config=quantization_config, device_map=self.configurations['device_map']
        )
        model.config.use_cache = False

        tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        tokenizer.add_special_tokens({'pad_token': '[PADDER]'})
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        return model, tokenizer

    def prepare_training_config(self):
        """Prepare the training configurations and parameters."""
        from transformers import TrainingArguments

        return TrainingArguments(
            output_dir=self.output_dir,
            **self.configurations
        )

    def setup_trainer(self, model, dataset, tokenizer, training_args):
        """Set up the trainer with the model, dataset, tokenizer, and training arguments."""
        peft_config = LoraConfig(
            lora_alpha=self.configurations['lora_alpha'],
            lora_dropout=self.configurations['lora_dropout'],
            r=self.configurations['lora_r'],
            bias="none",
            task_type="CAUSAL_LM",
        )

        return SFTTrainer(
            model=model,
            train_dataset=dataset,
            peft_config=peft_config,
            dataset_text_field="text",
            max_seq_length=self.configurations.get('max_seq_length', None),
            tokenizer=tokenizer,
            args=training_args,
            packing=self.configurations.get('packing', False),
        )

    def fine_tune(self):
        """Orchestrates the fine-tuning process."""
        dataset = self.load_dataset()
        quant_config = self.prepare_quantization_config()
        model, tokenizer = self.load_model_and_tokenizer(quant_config)
        training_args = self.prepare_training_config()
        trainer = self.setup_trainer(model, dataset, tokenizer, training_args)

        trainer.train()
        trainer.model.save_pretrained(self.new_model_name)

# To use the class
fine_tuner = LlamaFineTuner(
    model_name="NousResearch/Llama-2-7b-hf",
    dataset_name="mlabonne/guanaco-llama2-1k",
    new_model_name="llama-2-7b-test",
    output_dir="./results",
    lora_r=64,
    lora_alpha=16,
    lora_dropout=0.1,
    use_4bit=True,
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_quant_type="nf4",
    use_nested_quant=False,
    num_train_epochs=1,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=1,
    max_grad_norm=0.3,
    learning_rate=2e-4,
    weight_decay=0.001,
    optim="paged_adamw_32bit",
    lr_scheduler_type="constant",
    max_steps=-1,
    warmup_ratio=0.03,
    group_by_length=True,
    save_steps=25,
    logging_steps=25,
    device_map={"": 0}
)
fine_tuner.fine_tune()
