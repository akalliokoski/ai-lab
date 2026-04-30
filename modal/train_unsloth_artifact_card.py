from __future__ import annotations

"""
First GPU-backed Unsloth entrypoint for the ai-lab artifact-card project.

This task replaces the broad tutor adapter with a narrower structured-output job:
- read the local JSONL artifact-card dataset
- convert instruction/input/output rows into conversational records
- apply an Unsloth chat template
- run a short LoRA SFT job on Modal
- save the adapter and tokenizer to a persistent Modal volume
- save full base-vs-tuned eval outputs plus automatic JSON/field scoring

Important:
- HF_TOKEN must be configured before a real run is attempted.
- Keep the first run short and cheap. The goal is workflow validation and scoreable improvement.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

DEFAULT_MODEL_NAME = "unsloth/Llama-3.2-1B-Instruct-bnb-4bit"
DEFAULT_CHAT_TEMPLATE = "llama-3.2"
DEFAULT_SYSTEM_PROMPT = (
    "You are the Hermes AI Lab experiment card writer. Read the user evidence and return only one "
    "valid JSON object with exactly these keys: run_id, dataset_name, model_name, verdict, "
    "primary_failure_modes, key_evidence, next_action. Do not add prose before or after the JSON."
)
DEFAULT_DATASET_NAME = "artifact-card-v1"
LOCAL_DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
VOLUME_NAME = "ai-lab-unsloth-artifacts"
REMOTE_ARTIFACT_ROOT = Path("/artifacts")
DEFAULT_EXPECTED_FIELDS = [
    "run_id",
    "dataset_name",
    "model_name",
    "verdict",
    "primary_failure_modes",
    "key_evidence",
    "next_action",
]
DEFAULT_LIST_FIELDS = ["primary_failure_modes", "key_evidence"]
DEFAULT_TASK_CONFIG = {
    "system_prompt": DEFAULT_SYSTEM_PROMPT,
    "expected_fields": DEFAULT_EXPECTED_FIELDS,
    "list_fields": DEFAULT_LIST_FIELDS,
    "max_new_tokens": 220,
}

app = modal.App("ai-lab-unsloth-artifact-card")
artifacts_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch==2.10.0",
        "torchvision==0.25.0",
        "xformers==0.0.35",
    )
    .pip_install(
        "unsloth==2025.11.1",
        "transformers==4.57.2",
        "datasets==4.8.5",
        "trl==0.23.0",
        "accelerate==1.13.0",
        "peft==0.19.1",
        "huggingface_hub==0.36.2",
    )
)


def load_jsonl(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def row_to_user_content(row: dict[str, str]) -> str:
    user_content = row["instruction"].strip()
    if row.get("input"):
        user_content = f"{user_content}\n\nInput:\n{row['input'].strip()}"
    return user_content


def row_to_conversation(row: dict[str, str], system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": row_to_user_content(row)},
            {"role": "assistant", "content": row["output"].strip()},
        ]
    }


def load_task_config(dataset_dir: Path) -> dict[str, Any]:
    config_path = dataset_dir / "task_config.json"
    config = dict(DEFAULT_TASK_CONFIG)
    if config_path.exists():
        user_config = json.loads(config_path.read_text())
        config.update(user_config)
    config["expected_fields"] = list(config.get("expected_fields") or DEFAULT_EXPECTED_FIELDS)
    config["list_fields"] = list(config.get("list_fields") or [])
    config["max_new_tokens"] = int(config.get("max_new_tokens") or DEFAULT_TASK_CONFIG["max_new_tokens"])
    config["system_prompt"] = str(config.get("system_prompt") or DEFAULT_SYSTEM_PROMPT)
    return config


def load_local_payload(dataset_name: str = DEFAULT_DATASET_NAME) -> dict[str, Any]:
    dataset_dir = LOCAL_DATA_ROOT / dataset_name
    train_rows = load_jsonl(dataset_dir / "train.jsonl")
    eval_rows = load_jsonl(dataset_dir / "eval.jsonl")
    return {
        "train": train_rows,
        "eval": eval_rows,
        "dataset_name": dataset_dir.name,
        "dataset_dir": str(dataset_dir),
        "task_config": load_task_config(dataset_dir),
    }


def safe_json_parse(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().lower().split())


def normalize_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(normalize_text(item) for item in value)


def field_match(reference: dict[str, Any], candidate: dict[str, Any], field: str, list_fields: set[str]) -> bool:
    if field in list_fields:
        return normalize_list(reference.get(field)) == normalize_list(candidate.get(field))
    return normalize_text(reference.get(field)) == normalize_text(candidate.get(field))


def score_eval_rows(
    rows: list[dict[str, str]],
    response_key: str,
    expected_fields: list[str],
    list_fields: list[str],
) -> dict[str, Any]:
    total = len(rows)
    valid = 0
    exact = 0
    field_hits = {field: 0 for field in expected_fields}
    invalid_examples: list[dict[str, str]] = []
    list_field_set = set(list_fields)

    for row in rows:
        reference = safe_json_parse(row["reference"])
        candidate = safe_json_parse(row[response_key])
        if reference is None:
            raise ValueError("Reference eval output is not valid JSON")
        if candidate is None:
            invalid_examples.append(
                {
                    "instruction": row["instruction"],
                    "response": row[response_key],
                }
            )
            continue
        valid += 1
        row_exact = True
        for field in expected_fields:
            hit = field_match(reference, candidate, field, list_field_set)
            if hit:
                field_hits[field] += 1
            else:
                row_exact = False
        if row_exact:
            exact += 1

    return {
        "rows": total,
        "valid_json_rate": valid / total if total else 0.0,
        "exact_card_match_rate": exact / total if total else 0.0,
        "field_accuracy": {field: field_hits[field] / total if total else 0.0 for field in expected_fields},
        "invalid_examples": invalid_examples[:3],
    }


@app.function(
    gpu="T4",
    image=image,
    timeout=60 * 60,
    volumes={str(REMOTE_ARTIFACT_ROOT): artifacts_volume},
)
def run_first_sft(
    payload: dict[str, Any],
    model_name: str = DEFAULT_MODEL_NAME,
    chat_template: str = DEFAULT_CHAT_TEMPLATE,
    max_seq_length: int = 2048,
    learning_rate: float = 2e-4,
    max_steps: int = 20,
) -> dict[str, Any]:
    from datasets import Dataset
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import get_chat_template
    from trl import SFTConfig, SFTTrainer

    task_config = dict(payload.get("task_config") or DEFAULT_TASK_CONFIG)
    system_prompt = str(task_config.get("system_prompt") or DEFAULT_SYSTEM_PROMPT)
    expected_fields = list(task_config.get("expected_fields") or DEFAULT_EXPECTED_FIELDS)
    list_fields = list(task_config.get("list_fields") or [])
    max_new_tokens = int(task_config.get("max_new_tokens") or DEFAULT_TASK_CONFIG["max_new_tokens"])

    train_records = [row_to_conversation(row, system_prompt=system_prompt) for row in payload["train"]]
    eval_records = [row_to_conversation(row, system_prompt=system_prompt) for row in payload["eval"]]

    train_dataset = Dataset.from_list(train_records)
    eval_dataset = Dataset.from_list(eval_records)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )
    tokenizer = get_chat_template(tokenizer, chat_template=chat_template)

    def formatting_prompts_func(examples: dict[str, list[Any]]) -> dict[str, list[str]]:
        messages = examples["messages"]
        texts = [
            tokenizer.apply_chat_template(
                convo,
                tokenize=False,
                add_generation_prompt=False,
            )
            for convo in messages
        ]
        return {"text": texts}

    def render_generation_prompt(row: dict[str, str]) -> str:
        return tokenizer.apply_chat_template(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": row_to_user_content(row)},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )

    def generate_samples(current_model: Any, rows: list[dict[str, str]], label: str) -> list[dict[str, str]]:
        import torch

        FastLanguageModel.for_inference(current_model)
        results: list[dict[str, str]] = []
        for row in rows:
            prompt = render_generation_prompt(row)
            encoded = tokenizer(prompt, return_tensors="pt")
            encoded = {key: value.to(current_model.device) for key, value in encoded.items()}
            with torch.no_grad():
                generated = current_model.generate(
                    **encoded,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    use_cache=True,
                )
            prompt_tokens = encoded["input_ids"].shape[1]
            new_tokens = generated[0][prompt_tokens:]
            text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            results.append(
                {
                    "label": label,
                    "instruction": row["instruction"],
                    "reference": row["output"].strip(),
                    "response": text,
                }
            )
        if hasattr(FastLanguageModel, "for_training"):
            FastLanguageModel.for_training(current_model)
        return results

    train_dataset = train_dataset.map(formatting_prompts_func, batched=True)
    eval_dataset = eval_dataset.map(formatting_prompts_func, batched=True)

    sample_eval_rows = payload["eval"][:3]
    base_eval_samples = generate_samples(model, sample_eval_rows, label="base")
    base_eval_full = generate_samples(model, payload["eval"], label="base")

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
        max_seq_length=max_seq_length,
    )

    output_dir = "/tmp/ai-lab-unsloth-artifact-card-output"
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        args=SFTConfig(
            output_dir=output_dir,
            dataset_text_field="text",
            max_length=max_seq_length,
            dataset_num_proc=4,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=2,
            max_steps=max_steps,
            learning_rate=learning_rate,
            logging_steps=1,
            optim="adamw_8bit",
            seed=3407,
            report_to=[],
            save_strategy="no",
            assistant_only_loss=True,
        ),
    )

    trainer_stats = trainer.train()
    metrics = dict(trainer_stats.metrics)
    tuned_eval_samples = generate_samples(model, sample_eval_rows, label="tuned")
    tuned_eval_full = generate_samples(model, payload["eval"], label="tuned")

    full_eval_rows = [
        {
            "instruction": base_sample["instruction"],
            "reference": base_sample["reference"],
            "base_response": base_sample["response"],
            "tuned_response": tuned_sample["response"],
        }
        for base_sample, tuned_sample in zip(base_eval_full, tuned_eval_full, strict=True)
    ]

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_dir = REMOTE_ARTIFACT_ROOT / payload["dataset_name"] / run_id
    adapter_dir = artifact_dir / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)

    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    result = {
        "status": "trained",
        "run_id": run_id,
        "dataset_name": payload["dataset_name"],
        "train_rows": len(payload["train"]),
        "eval_rows": len(payload["eval"]),
        "model_name": model_name,
        "chat_template": chat_template,
        "max_seq_length": max_seq_length,
        "max_steps": max_steps,
        "task_config": {
            "system_prompt": system_prompt,
            "expected_fields": expected_fields,
            "list_fields": list_fields,
            "max_new_tokens": max_new_tokens,
        },
        "output_dir": output_dir,
        "artifact_volume": VOLUME_NAME,
        "artifact_dir": str(artifact_dir),
        "adapter_dir": str(adapter_dir),
        "metrics": metrics,
        "sample_eval": [
            {
                "instruction": base_sample["instruction"],
                "reference": base_sample["reference"],
                "base_response": base_sample["response"],
                "tuned_response": tuned_sample["response"],
            }
            for base_sample, tuned_sample in zip(base_eval_samples, tuned_eval_samples, strict=True)
        ],
        "full_eval": full_eval_rows,
        "auto_eval": {
            "base_metrics": score_eval_rows(full_eval_rows, "base_response", expected_fields, list_fields),
            "tuned_metrics": score_eval_rows(full_eval_rows, "tuned_response", expected_fields, list_fields),
        },
        "trainer_config": {
            "per_device_train_batch_size": 2,
            "gradient_accumulation_steps": 4,
            "effective_batch_size": 8,
            "assistant_only_loss": True,
            "learning_rate": learning_rate,
            "warmup_steps": 2,
        },
        "next_steps": [
            "Review auto_eval.tuned_metrics before trusting train loss.",
            "Inspect rows where the tuned output is invalid JSON or misses required fields.",
            "Patch the dataset by field failure, not by train loss alone.",
        ],
    }

    (artifact_dir / "run_summary.json").write_text(json.dumps(result, indent=2))
    artifacts_volume.commit()

    result["artifact_files"] = sorted(
        str(path.relative_to(artifact_dir))
        for path in artifact_dir.rglob("*")
        if path.is_file()
    )
    return result


@app.local_entrypoint()
def main(
    model_name: str = DEFAULT_MODEL_NAME,
    chat_template: str = DEFAULT_CHAT_TEMPLATE,
    dataset_name: str = DEFAULT_DATASET_NAME,
    max_steps: int = 20,
) -> None:
    dataset_dir = LOCAL_DATA_ROOT / dataset_name
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Missing dataset directory: {dataset_dir}")
    payload = load_local_payload(dataset_name=dataset_name)
    print(
        run_first_sft.remote(
            payload,
            model_name=model_name,
            chat_template=chat_template,
            max_steps=max_steps,
        )
    )
