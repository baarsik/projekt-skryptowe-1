"""Package one Git revision of the backend with its tested dependency versions."""

import argparse
import io
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def create_package(
    repository: Path, revision: str, output: Path, requirements: str
) -> None:
    source_archive = subprocess.check_output(
        [
            "git",
            "-C",
            str(repository),
            "archive",
            "--format=zip",
            f"{revision}:backend",
        ]
    )

    with ZipFile(io.BytesIO(source_archive)) as source:
        with ZipFile(output, "w", ZIP_DEFLATED) as package:
            for entry in source.infolist():
                if entry.filename == "requirements.txt":
                    continue
                if entry.filename.startswith("tests/"):
                    continue
                package.writestr(entry, source.read(entry))
            package.writestr("requirements.txt", requirements)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    tested_requirements = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"], text=True
    )
    create_package(
        arguments.repository.resolve(),
        arguments.revision,
        arguments.output.resolve(),
        tested_requirements,
    )
    print(f"Backend deployment package: {arguments.output}")
