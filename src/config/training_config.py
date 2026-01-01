from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional


class DatasetConfig(BaseModel):
    path: str
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    shuffle: bool = True
    seed: int = 42


class TrainingParameters(BaseModel):
    epochs: int = 1
    batch_size: int = 1
    gradient_accumulation_steps: int = 1
    learning_rate: float = 1e-5
    warmup_steps: int = 0
    weight_decay: float = 0.0
    optimizer: str = "adamw"
    beta1: float = 0.9
    beta2: float = 0.999
    epsilon: float = 1e-8
    scheduler: Optional[str] = None
    num_cycles: Optional[float] = None


class LoRAConfig(BaseModel):
    enabled: bool = False
    r: int = 8
    alpha: int = 16
    dropout: float = 0.0
    target_modules: List[str] = Field(default_factory=list)


class QuantizationConfig(BaseModel):
    enabled: bool = False
    bits: int = 8
    group_size: int = 128
    desc_act: bool = False


class CheckpointConfig(BaseModel):
    save_strategy: str = "epoch"
    save_steps: int = 0
    save_total_limit: Optional[int] = None
    load_best_model_at_end: bool = False
    metric_for_best_model: Optional[str] = None


class EvaluationConfig(BaseModel):
    eval_strategy: str = "epoch"
    eval_steps: int = 0
    per_device_eval_batch_size: int = 1


class LoggingConfig(BaseModel):
    strategy: str = "steps"
    steps: int = 100
    report_to: str = "tensorboard"
    logging_dir: str = "./logs"


class OutputConfig(BaseModel):
    dir: str = "./output"
    save_format: str = "pt"
    push_to_hub: bool = False
    hub_model_id: Optional[str] = None


class HardwareConfig(BaseModel):
    device: str = "auto"
    fp16: bool = False
    bf16: bool = False
    gradient_checkpointing: bool = False
    use_cpu: bool = False


class EarlyStoppingConfig(BaseModel):
    enabled: bool = False
    patience: int = 0
    threshold: float = 0.0


class TrainingConfig(BaseModel):
    base_model: str
    model_type: Optional[str] = "causal"
    dataset: DatasetConfig
    parameters: TrainingParameters
    lora: LoRAConfig = LoRAConfig()
    quantization: QuantizationConfig = QuantizationConfig()
    checkpoint: CheckpointConfig = CheckpointConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    logging: LoggingConfig = LoggingConfig()
    output: OutputConfig = OutputConfig()
    hardware: HardwareConfig = HardwareConfig()
    early_stopping: EarlyStoppingConfig = EarlyStoppingConfig()


def validate_training_config(data: dict) -> TrainingConfig:
    try:
        cfg = TrainingConfig(**data.get("training", {}))
        return cfg
    except ValidationError as e:
        raise
