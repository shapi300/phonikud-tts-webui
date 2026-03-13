#!/usr/bin/env python3
"""Download required models for Phonikud TTS."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def download_file(url: str, output_path: str) -> bool:
    """Download a file using curl or wget."""
    print(f"Downloading {url} -> {output_path}")

    # Create parent directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Try curl first, then wget
    try:
        result = subprocess.run(
            ["curl", "-L", "-o", output_path, url],
            check=True,
            capture_output=True,
        )
        print(f"✓ Downloaded {output_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        result = subprocess.run(
            ["wget", "-O", output_path, url],
            check=True,
            capture_output=True,
        )
        print(f"✓ Downloaded {output_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print(f"✗ Failed to download {output_path}")
    return False


def extract_tarball(tar_path: str, output_dir: str) -> bool:
    """Extract a tar.gz file."""
    print(f"Extracting {tar_path} -> {output_dir}")
    try:
        subprocess.run(
            ["tar", "-xf", tar_path, "-C", output_dir],
            check=True,
        )
        print(f"✓ Extracted {tar_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to extract {tar_path}: {e}")
        return False


def download_phonikud(models_dir: Path) -> bool:
    """Download Phonikud model."""
    print("\n=== Downloading Phonikud Model ===")

    model_path = models_dir / "phonikud-1.0.int8.onnx"

    if model_path.exists():
        print(f"✓ Phonikud model already exists at {model_path}")
        return True

    url = "https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx"
    return download_file(url, str(model_path))


def download_piper(models_dir: Path, model_name: str = "shaul") -> bool:
    """Download Piper TTS model."""
    print(f"\n=== Downloading Piper Model ({model_name}) ===")

    piper_dir = models_dir / "piper"
    piper_dir.mkdir(parents=True, exist_ok=True)

    model_path = piper_dir / f"{model_name}.onnx"
    config_path = piper_dir / "model.config.json"

    success = True

    # Download model if not exists
    if not model_path.exists():
        url = f"https://huggingface.co/thewh1teagle/phonikud-tts-checkpoints/resolve/main/{model_name}.onnx"
        if not download_file(url, str(model_path)):
            success = False
    else:
        print(f"✓ Piper model already exists at {model_path}")

    # Download config if not exists
    if not config_path.exists():
        url = "https://huggingface.co/thewh1teagle/phonikud-tts-checkpoints/resolve/main/model.config.json"
        if not download_file(url, str(config_path)):
            success = False
    else:
        print(f"✓ Piper config already exists at {config_path}")

    return success


def download_zipvoice(models_dir: Path, include_prompts: bool = True) -> bool:
    """Download ZipVoice TTS model."""
    print("\n=== Downloading ZipVoice Model ===")

    zipvoice_dir = models_dir / "zipvoice"
    tar_path = models_dir / "zipvoice-onnx.tar.gz"

    # Check if already extracted
    text_encoder = zipvoice_dir / "text_encoder.onnx"
    if text_encoder.exists():
        print(f"✓ ZipVoice model already exists at {zipvoice_dir}")
        return True

    success = True

    # Download and extract model tarball
    url = "https://huggingface.co/thewh1teagle/zipvoice-heb/resolve/main/zipvoice-onnx.tar.gz"
    if download_file(url, str(tar_path)):
        if not extract_tarball(str(tar_path), str(models_dir)):
            success = False
        else:
            # Clean up tarball
            tar_path.unlink()
    else:
        success = False

    # Download prompts
    if include_prompts:
        prompts_dir = zipvoice_dir / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        prompt_files = [
            ("prompt_hebrew_male1.wav", "prompt.wav"),
        ]

        for filename, output_name in prompt_files:
            prompt_path = prompts_dir / output_name
            if not prompt_path.exists():
                url = f"https://github.com/thewh1teagle/zipvoice-onnx/releases/download/model-files-v1.0/{filename}"
                download_file(url, str(prompt_path))

    return success


def main():
    parser = argparse.ArgumentParser(description="Download Phonikud TTS models")
    parser.add_argument(
        "--output",
        "-o",
        default="api/models",
        help="Output directory for models",
    )
    parser.add_argument(
        "--piper-only",
        action="store_true",
        help="Only download Piper model",
    )
    parser.add_argument(
        "--zipvoice-only",
        action="store_true",
        help="Only download ZipVoice model",
    )
    parser.add_argument(
        "--no-prompts",
        action="store_true",
        help="Skip downloading ZipVoice prompt files",
    )

    args = parser.parse_args()

    models_dir = Path(args.output)
    models_dir.mkdir(parents=True, exist_ok=True)

    print(f"Models directory: {models_dir.absolute()}")

    success = True

    if args.zipvoice_only:
        if not download_zipvoice(models_dir, include_prompts=not args.no_prompts):
            success = False
    elif args.piper_only:
        if not download_piper(models_dir):
            success = False
    else:
        # Download all models
        if not download_phonikud(models_dir):
            success = False
        if not download_piper(models_dir):
            success = False
        if not download_zipvoice(models_dir, include_prompts=not args.no_prompts):
            success = False

    print("\n" + "=" * 50)
    if success:
        print("✓ All models downloaded successfully!")
        print(f"\nModels location: {models_dir.absolute()}")
    else:
        print("✗ Some models failed to download")
        sys.exit(1)


if __name__ == "__main__":
    main()