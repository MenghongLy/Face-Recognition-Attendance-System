from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import face_recognition


def build_encodings(students_dir: Path, output_file: Path) -> None:
	"""Build face encodings from images in students_dir and save to output_file."""
	if not students_dir.exists():
		raise FileNotFoundError(f"Students folder not found: {students_dir}")

	image_paths = [
		p
		for p in students_dir.iterdir()
		if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
	]

	if not image_paths:
		raise RuntimeError(
			"No student images found. Add images to the students folder first."
		)

	known_names: list[str] = []
	known_encodings: list[list[float]] = []

	for image_path in sorted(image_paths):
		name = image_path.stem
		image = face_recognition.load_image_file(str(image_path))
		encodings = face_recognition.face_encodings(image)

		if not encodings:
			print(f"[WARN] No face found in {image_path.name}. Skipping.")
			continue

		if len(encodings) > 1:
			print(
				f"[WARN] Multiple faces found in {image_path.name}. Using first face only."
			)

		known_names.append(name)
		known_encodings.append(encodings[0])
		print(f"[OK] Encoded: {name}")

	if not known_encodings:
		raise RuntimeError("No valid face encodings produced. Check your student images.")

	payload = {"names": known_names, "encodings": known_encodings}
	with output_file.open("wb") as f:
		pickle.dump(payload, f)

	print(f"\nSaved {len(known_names)} face encodings to {output_file}")


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Build face encodings for students.")
	parser.add_argument(
		"--students-dir",
		type=Path,
		default=Path("students"),
		help="Folder containing student face images.",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=Path("encodings.pkl"),
		help="Output pickle file for face encodings.",
	)
	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	build_encodings(args.students_dir, args.output)
