from __future__ import annotations

import argparse
import pickle
from datetime import datetime
from pathlib import Path

import cv2
import face_recognition
import numpy as np

from attendance import AttendanceManager


def parse_time(value: str) -> datetime.time:
	return datetime.strptime(value, "%H:%M").time()


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Face recognition attendance system")
	parser.add_argument(
		"--encodings",
		type=Path,
		default=Path("encodings.pkl"),
		help="Path to generated face encodings pickle file.",
	)
	parser.add_argument(
		"--excel",
		type=Path,
		default=Path("attendance") / "attendance.xlsx",
		help="Path to output Excel attendance file.",
	)
	parser.add_argument(
		"--on-time",
		type=parse_time,
		default=parse_time("07:00"),
		help="On-time cutoff in HH:MM format (default: 07:00).",
	)
	parser.add_argument(
		"--late-cutoff",
		type=parse_time,
		default=parse_time("07:30"),
		help="Late cutoff in HH:MM format (default: 07:30).",
	)
	parser.add_argument(
		"--camera-index",
		type=int,
		default=0,
		help="Camera index (default: 0).",
	)
	parser.add_argument(
		"--tolerance",
		type=float,
		default=0.5,
		help="Face match tolerance (lower means stricter match).",
	)
	return parser.parse_args()


def load_known_faces(encodings_file: Path) -> tuple[list[str], list[np.ndarray]]:
	if not encodings_file.exists():
		raise FileNotFoundError(
			f"Encodings file not found: {encodings_file}. Run encoder.py first."
		)

	with encodings_file.open("rb") as f:
		payload = pickle.load(f)

	names = payload.get("names", [])
	encodings = payload.get("encodings", [])

	if not names or not encodings:
		raise RuntimeError("No known faces in encodings file.")

	return names, encodings


def main() -> None:
	args = parse_args()
	names, known_encodings = load_known_faces(args.encodings)

	if args.on_time > args.late_cutoff:
		raise ValueError("--on-time must be earlier than or equal to --late-cutoff")

	attendance = AttendanceManager(
		excel_file=args.excel,
		on_time_cutoff=args.on_time,
		late_cutoff=args.late_cutoff,
	)

	cap = cv2.VideoCapture(args.camera_index)
	if not cap.isOpened():
		raise RuntimeError("Could not open webcam.")

	print("Camera started. Press 'q' to quit.")
	print(f"On time <= {args.on_time.strftime('%H:%M')}")
	print(f"Late <= {args.late_cutoff.strftime('%H:%M')}")

	session_seen: set[str] = set()

	try:
		while True:
			success, frame = cap.read()
			if not success:
				print("[WARN] Failed to read frame from camera.")
				continue

			small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
			rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

			face_locations = face_recognition.face_locations(rgb_small)
			face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

			for face_encoding, face_location in zip(face_encodings, face_locations):
				matches = face_recognition.compare_faces(
					known_encodings, face_encoding, tolerance=args.tolerance
				)
				face_distances = face_recognition.face_distance(
					known_encodings, face_encoding
				)

				name = "Unknown"
				status_text = ""

				if len(face_distances) > 0:
					best_match_idx = int(np.argmin(face_distances))
					if matches[best_match_idx]:
						name = names[best_match_idx]

						if name not in session_seen:
							result = attendance.mark_attendance(name)
							session_seen.add(name)

							if result.already_marked:
								status_text = "Already Marked Today"
								print(f"[SKIP] {name} already marked today.")
							else:
								status_text = result.status
								print(
									f"[MARKED] {name} at "
									f"{result.check_in_time.strftime('%H:%M:%S')} ({result.status})"
								)

				top, right, bottom, left = face_location
				top, right, bottom, left = (
					top * 4,
					right * 4,
					bottom * 4,
					left * 4,
				)

				color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
				cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

				label = name if not status_text else f"{name} | {status_text}"
				cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
				cv2.putText(
					frame,
					label,
					(left + 6, bottom - 6),
					cv2.FONT_HERSHEY_SIMPLEX,
					0.5,
					(255, 255, 255),
					1,
				)

			cv2.imshow("Face Attendance", frame)
			if cv2.waitKey(1) & 0xFF == ord("q"):
				break
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == "__main__":
	main()
