from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path

import pandas as pd


@dataclass
class AttendanceResult:
	name: str
	check_in_time: datetime
	status: str
	already_marked: bool


class AttendanceManager:
	def __init__(
		self,
		excel_file: Path,
		on_time_cutoff: time,
		late_cutoff: time,
	) -> None:
		self.excel_file = excel_file
		self.on_time_cutoff = on_time_cutoff
		self.late_cutoff = late_cutoff
		self._ensure_excel_exists()

	def _ensure_excel_exists(self) -> None:
		if self.excel_file.exists():
			return
		self.excel_file.parent.mkdir(parents=True, exist_ok=True)
		df = pd.DataFrame(columns=["Name", "Date", "CheckInTime", "Status"])
		df.to_excel(self.excel_file, index=False)

	def _load_df(self) -> pd.DataFrame:
		if not self.excel_file.exists():
			self._ensure_excel_exists()
		return pd.read_excel(self.excel_file)

	def _compute_status(self, now: datetime) -> str:
		current = now.time()
		if current <= self.on_time_cutoff:
			return "On Time"
		if current <= self.late_cutoff:
			return "Late"
		return "Too Late"

	def mark_attendance(self, name: str) -> AttendanceResult:
		now = datetime.now()
		today = now.date().isoformat()

		df = self._load_df()
		if not df.empty:
			already = (
				(df["Name"].astype(str).str.lower() == name.lower())
				& (df["Date"].astype(str) == today)
			).any()
			if already:
				status = self._compute_status(now)
				return AttendanceResult(
					name=name,
					check_in_time=now,
					status=status,
					already_marked=True,
				)

		status = self._compute_status(now)
		new_row = {
			"Name": name,
			"Date": today,
			"CheckInTime": now.strftime("%H:%M:%S"),
			"Status": status,
		}

		df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
		df.to_excel(self.excel_file, index=False)

		return AttendanceResult(
			name=name,
			check_in_time=now,
			status=status,
			already_marked=False,
		)
