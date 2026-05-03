from __future__ import annotations

import json
import sys
from pathlib import Path


def best_model_name(payload: dict) -> str:
    best_name = None
    best_score = float('-inf')
    for model_name, body in payload.get('models', {}).items():
        score = body.get('summary', {}).get('balanced_accuracy')
        if score is None:
            continue
        if score > best_score:
            best_name = model_name
            best_score = score
    if best_name is None:
        raise ValueError('No model summaries found in payload')
    return best_name


def format_summary(payload: dict) -> str:
    model_name = best_model_name(payload)
    summary = payload['models'][model_name]['summary']
    return (
        f"cv={payload['cv']} | best_model={model_name} | "
        f"balanced_accuracy={summary['balanced_accuracy']:.3f} | "
        f"sensitivity={summary['sensitivity']:.3f} | "
        f"specificity={summary['specificity']:.3f} | "
        f"auroc={summary['auroc'] if summary['auroc'] is not None else 'n/a'}"
    )


def compare(first: dict, second: dict) -> dict[str, float | None]:
    first_model = best_model_name(first)
    second_model = best_model_name(second)
    first_summary = first['models'][first_model]['summary']
    second_summary = second['models'][second_model]['summary']
    gap = {}
    for key in ['balanced_accuracy', 'sensitivity', 'specificity']:
        gap[key] = round(first_summary[key] - second_summary[key], 6)
    if first_summary['auroc'] is None or second_summary['auroc'] is None:
        gap['auroc'] = None
    else:
        gap['auroc'] = round(first_summary['auroc'] - second_summary['auroc'], 6)
    return gap


def main(paths: list[str]) -> None:
    if len(paths) not in {1, 2}:
        raise SystemExit('Usage: python3 eval.py <metrics.json> [<metrics.json>]')

    payloads = [json.loads(Path(path).read_text()) for path in paths]
    for path, payload in zip(paths, payloads):
        print(f"{path}: {format_summary(payload)}")
    if len(payloads) == 2:
        gap = compare(payloads[0], payloads[1])
        print('gap(first-second):')
        print(json.dumps(gap, indent=2))


if __name__ == '__main__':
    main(sys.argv[1:])
