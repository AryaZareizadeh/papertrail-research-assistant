"""One durable transaction, with recoverable JSONL/manifest exports."""

import json

from evidence_assistant.data import file_hash, read_jsonl, text_hash, write_json, write_jsonl


def _hash(value):
    return text_hash(json.dumps(value, sort_keys=True))


def atomic_json(path, value, *, json_writer=None):
    temporary = path.with_name(path.name + ".tmp")
    (json_writer or write_json)(temporary, value)
    temporary.replace(path)


def save_checkpoint(output, saved, rows, *, json_writer=None):
    prediction_path = output / "predictions.jsonl"
    temporary = prediction_path.with_suffix(".tmp")
    write_jsonl(temporary, rows)
    newer = {**saved, "prediction_sha256": file_hash(temporary)}
    atomic_json(
        output / "checkpoint.json",
        {"manifest": newer, "rows": rows, "rows_sha256": _hash(rows)},
        json_writer=json_writer,
    )
    temporary.replace(prediction_path)
    atomic_json(output / "manifest.json", newer, json_writer=json_writer)
    return newer


def restore_checkpoint(output, saved, *, json_writer=None):
    checkpoint_path, prediction_path = output / "checkpoint.json", output / "predictions.jsonl"
    if not checkpoint_path.exists():
        rows = read_jsonl(prediction_path) if prediction_path.exists() else []
        if rows and file_hash(prediction_path) != saved.get("prediction_sha256"):
            raise ValueError("Run predictions changed")
        return saved, rows
    checkpoint = json.loads(checkpoint_path.read_text("utf-8"))
    newer, rows = checkpoint["manifest"], checkpoint["rows"]
    # Only the prediction hash may lag publication; other manifest drift is rejected.
    old_metadata = {k: v for k, v in saved.items() if k != "prediction_sha256"}
    new_metadata = {k: v for k, v in newer.items() if k != "prediction_sha256"}
    if old_metadata != new_metadata or checkpoint["rows_sha256"] != _hash(rows):
        raise ValueError("Run checkpoint changed")
    if prediction_path.exists() and file_hash(prediction_path) not in {
        saved.get("prediction_sha256"),
        newer["prediction_sha256"],
    }:
        raise ValueError("Run predictions changed")
    temporary = prediction_path.with_suffix(".tmp")
    write_jsonl(temporary, rows)
    if file_hash(temporary) != newer["prediction_sha256"]:
        raise ValueError("Run checkpoint prediction hash changed")
    temporary.replace(prediction_path)
    atomic_json(output / "manifest.json", newer, json_writer=json_writer)
    return newer, rows
