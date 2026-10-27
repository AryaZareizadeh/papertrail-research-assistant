"""Export prepared runtime assets for a Linux container without benchmark labels."""

import argparse
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from evidence_assistant.config import load_config
from evidence_assistant.data import file_hash, write_json


def _relative_name(value):
    path = Path(value)
    if path.is_absolute() or path.name != value or "/" in value or "\\" in value:
        raise ValueError("Vector file must be a local artifact filename")
    return value


def export_runtime(config, output: Path):
    output = output.resolve()
    if output.exists():
        raise ValueError("Export output already exists; choose a new directory")
    original = config.artifact_dir.resolve()
    if output.is_relative_to(original) or original.is_relative_to(output):
        raise ValueError("Export output must be separate from the original artifacts")
    index = json.loads((original / "index_manifest.json").read_text("utf-8"))
    vector = _relative_name(index["vector_file"])
    embedding = json.loads((original / "embedding_model.json").read_text("utf-8"))
    generation = json.loads((original / "generation_tokenizer.json").read_text("utf-8"))
    model_root = Path(embedding["snapshot"]).resolve()
    tokenizer_root = Path(generation["snapshot"]).resolve()
    for source in (model_root, tokenizer_root):
        if output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError("Export output must be separate from prepared model snapshots")
    if not (model_root / "model.safetensors").is_file():
        raise ValueError("Prepare the pinned embedding weights before exporting")
    for name, expected in generation["file_hashes"].items():
        normalized = name.replace("\\", "/")
        if Path(name).is_absolute() or ".." in normalized.split("/"):
            raise ValueError("Tokenizer filename must stay inside its prepared snapshot")
        if file_hash(tokenizer_root / name) != expected:
            raise ValueError("Prepared generation tokenizer bytes changed")
    names = [
        "corpus.sqlite",
        "chunking_manifest.json",
        "index_manifest.json",
        vector,
        "generation_token_calibration.json",
    ]
    for name in names:
        if not (original / name).is_file():
            raise ValueError(f"Missing prepared runtime asset: {name}")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Staging and destination are resolved siblings under the explicitly chosen
    # output parent. Publication never moves/deletes the original asset directory.
    with TemporaryDirectory(prefix=".papertrail-export-", dir=output.parent) as temp:
        staging = Path(temp).resolve()
        if staging.parent != output.parent:
            raise ValueError("Export staging directory escaped its output parent")
        for name in names:
            shutil.copyfile(original / name, staging / name)
            if file_hash(staging / name) != file_hash(original / name):
                raise ValueError("Copied runtime asset hash mismatch")
        for source, relative in (
            (model_root, "models/embedding"),
            (tokenizer_root, "models/generation"),
        ):
            for file in source.rglob("*"):
                if not file.is_file():
                    continue
                destination = staging / relative / file.relative_to(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, destination)
                if file_hash(file) != file_hash(destination):
                    raise ValueError("Copied model asset hash mismatch")
        embedding["snapshot"] = "/artifacts/models/embedding"
        generation["snapshot"] = "/artifacts/models/generation"
        write_json(staging / "embedding_model.json", embedding)
        write_json(staging / "generation_tokenizer.json", generation)
        result = {
            "format": "papertrail-container-assets-v1",
            "source_metadata_hashes": {
                name: file_hash(original / name)
                for name in ("embedding_model.json", "generation_tokenizer.json")
            },
            "file_hashes": {
                file.relative_to(staging).as_posix(): file_hash(file)
                for file in sorted(staging.rglob("*"))
                if file.is_file()
            },
        }
        write_json(staging / "bundle_manifest.json", result)
        staging.rename(output)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--output", type=Path, default=Path("runtime/artifacts"))
    args = parser.parse_args()
    result = export_runtime(load_config(args.config), args.output)
    print(f"Exported {len(result['file_hashes'])} verified runtime files to {args.output}")


if __name__ == "__main__":
    main()
