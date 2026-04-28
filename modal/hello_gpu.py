from __future__ import annotations

import modal

app = modal.App("ai-lab-hello-gpu")
image = modal.Image.debian_slim().pip_install("torch", "transformers")

@app.function(gpu="T4", image=image)
def hello_gpu(prompt: str = "Explain LoRA in 5 short bullets.") -> dict:
    return {
        "message": "Modal GPU function reached successfully.",
        "prompt": prompt,
    }

@app.local_entrypoint()
def main(prompt: str = "Explain LoRA in 5 short bullets."):
    print(hello_gpu.remote(prompt))
