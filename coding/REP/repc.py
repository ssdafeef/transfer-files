import sqlite3
from datetime import date, datetime
from pathlib import Path

import streamlit as st


DB_PATH = Path(__file__).with_name("workout_reps.db")


def get_connection():
	"""Create a SQLite connection with rows as dictionaries."""
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn


def init_db():
	"""Create tables and migrate existing exercise names into the catalog."""
	with get_connection() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS exercises (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL UNIQUE,
				created_at TEXT NOT NULL
			)
			"""
		)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS workouts (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				session_date TEXT NOT NULL,
				exercise_name TEXT NOT NULL,
				set_number INTEGER NOT NULL,
				reps_count INTEGER NOT NULL,
				weight_used REAL NOT NULL DEFAULT 0,
				created_at TEXT NOT NULL
			)
			"""
		)

		# Backward compatible migration for existing databases.
		columns = conn.execute("PRAGMA table_info(workouts)").fetchall()
		column_names = {column[1] for column in columns}
		if "weight_used" not in column_names:
			conn.execute(
				"ALTER TABLE workouts ADD COLUMN weight_used REAL NOT NULL DEFAULT 0"
			)

		# Seed permanent exercise catalog from any existing workouts.
		distinct_names = conn.execute(
			"SELECT DISTINCT exercise_name FROM workouts"
		).fetchall()
		now_iso = datetime.now().isoformat(timespec="seconds")
		for row in distinct_names:
			name = (row["exercise_name"] or "").strip()
			if name:
				conn.execute(
					"INSERT OR IGNORE INTO exercises (name, created_at) VALUES (?, ?)",
					(name, now_iso),
				)
		conn.commit()


def get_exercise_names():
	"""Return permanent exercise names sorted alphabetically."""
	with get_connection() as conn:
		rows = conn.execute("SELECT name FROM exercises ORDER BY name ASC").fetchall()
	return [row["name"] for row in rows]


def add_exercise(exercise_name):
	"""Create a new exercise in the permanent exercise list."""
	name = exercise_name.strip()
	if not name:
		return False, "Exercise name cannot be empty."

	now_iso = datetime.now().isoformat(timespec="seconds")
	with get_connection() as conn:
		conn.execute(
			"INSERT OR IGNORE INTO exercises (name, created_at) VALUES (?, ?)",
			(name, now_iso),
		)
		created = conn.total_changes > 0
		conn.commit()

	if created:
		return True, f"Exercise '{name}' added."
	return False, f"Exercise '{name}' already exists."


def remove_exercise(exercise_name, delete_history=False):
	"""Remove an exercise from catalog, optionally deleting its workout history."""
	name = exercise_name.strip()
	if not name:
		return False, "Please choose an exercise to remove."

	with get_connection() as conn:
		conn.execute("DELETE FROM exercises WHERE name = ?", (name,))
		if delete_history:
			conn.execute("DELETE FROM workouts WHERE exercise_name = ?", (name,))
		removed = conn.total_changes > 0
		conn.commit()

	if not removed:
		return False, f"Exercise '{name}' was not found."

	if delete_history:
		return True, f"Exercise '{name}' and its workout history were removed."
	return True, f"Exercise '{name}' was removed from your exercise list."


def add_workout_session(session_date, exercise_name, reps_by_set, weights_by_set):
	"""Insert one row per set for a single workout session."""
	now_iso = datetime.now().isoformat(timespec="seconds")
	records = [
		(session_date, exercise_name, index + 1, reps, weights_by_set[index], now_iso)
		for index, reps in enumerate(reps_by_set)
	]
	with get_connection() as conn:
		conn.executemany(
			"""
			INSERT INTO workouts (session_date, exercise_name, set_number, reps_count, weight_used, created_at)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			records,
		)
		conn.commit()


def get_workout_rows(start_date=None, end_date=None, exercise_name=None):
	"""Fetch workout set rows with optional date and exercise filtering."""
	query = """
		SELECT id, session_date, exercise_name, set_number, reps_count, weight_used, created_at
		FROM workouts
		WHERE 1=1
	"""
	params = []

	if start_date:
		query += " AND session_date >= ?"
		params.append(start_date)
	if end_date:
		query += " AND session_date <= ?"
		params.append(end_date)
	if exercise_name and exercise_name != "All":
		query += " AND exercise_name = ?"
		params.append(exercise_name)

	query += " ORDER BY session_date DESC, exercise_name ASC, set_number ASC"

	with get_connection() as conn:
		rows = conn.execute(query, params).fetchall()

	return [dict(row) for row in rows]


def get_session_choices():
	"""Return distinct workout sessions for selecting and editing."""
	with get_connection() as conn:
		rows = conn.execute(
			"""
			SELECT session_date, exercise_name,
				   COUNT(*) AS total_sets,
				   SUM(reps_count) AS total_reps
			FROM workouts
			GROUP BY session_date, exercise_name
			ORDER BY session_date DESC, exercise_name ASC
			"""
		).fetchall()
	return [dict(row) for row in rows]


def get_session_sets(session_date, exercise_name):
	"""Return reps and weight list for one session ordered by set number."""
	with get_connection() as conn:
		rows = conn.execute(
			"""
			SELECT reps_count, weight_used
			FROM workouts
			WHERE session_date = ? AND exercise_name = ?
			ORDER BY set_number ASC
			""",
			(session_date, exercise_name),
		).fetchall()
	return [
		{"reps": int(row["reps_count"]), "weight": float(row["weight_used"])}
		for row in rows
	]


def replace_workout_session(session_date, exercise_name, reps_by_set, weights_by_set):
	"""Replace all set rows for a session with updated set count and reps."""
	now_iso = datetime.now().isoformat(timespec="seconds")
	with get_connection() as conn:
		conn.execute(
			"DELETE FROM workouts WHERE session_date = ? AND exercise_name = ?",
			(session_date, exercise_name),
		)
		records = [
			(session_date, exercise_name, index + 1, reps, weights_by_set[index], now_iso)
			for index, reps in enumerate(reps_by_set)
		]
		conn.executemany(
			"""
			INSERT INTO workouts (session_date, exercise_name, set_number, reps_count, weight_used, created_at)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			records,
		)
		conn.commit()


def delete_workout_session(session_date, exercise_name):
	"""Delete all rows for one workout session."""
	with get_connection() as conn:
		conn.execute(
			"DELETE FROM workouts WHERE session_date = ? AND exercise_name = ?",
			(session_date, exercise_name),
		)
		conn.commit()


def build_session_totals(rows):
	"""Aggregate rows to totals grouped by date and exercise."""
	totals = {}
	for row in rows:
		key = (row["session_date"], row["exercise_name"])
		if key not in totals:
			totals[key] = {
				"Date": row["session_date"],
				"Exercise": row["exercise_name"],
				"Total Reps": 0,
				"Total Sets": 0,
			}
		totals[key]["Total Reps"] += int(row["reps_count"])
		totals[key]["Total Sets"] += 1

	return sorted(
		totals.values(), key=lambda item: (item["Date"], item["Exercise"]), reverse=True
	)


def build_progress_points(rows):
	"""Create points for charting total reps over time."""
	grouped = {}
	for row in rows:
		key = (row["session_date"], row["exercise_name"])
		grouped[key] = grouped.get(key, 0) + int(row["reps_count"])

	points = []
	for (session_date, exercise_name), total_reps in grouped.items():
		points.append(
			{
				"date": session_date,
				"exercise": exercise_name,
				"total_reps": total_reps,
			}
		)
	points.sort(key=lambda item: (item["date"], item["exercise"]))


def inject_styles():
	"""Apply a modern, mobile-friendly style layer to the app."""
	st.markdown(
		"""
		<style>
		.block-container {
			padding-top: 1.1rem;
			padding-bottom: 2rem;
			max-width: 1080px;
		}
		.app-card {
			border: 1px solid #dde6ef;
			border-radius: 18px;
			padding: 1rem;
			background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
			box-shadow: 0 8px 20px rgba(30, 70, 120, 0.08);
			margin-bottom: 1rem;
		}
		.app-subtitle {
			color: #4a6076;
			margin-bottom: 0.8rem;
		}
		@media (max-width: 720px) {
			.block-container {
				padding-left: 0.8rem;
				padding-right: 0.8rem;
			}
		}
		</style>
		""",
		unsafe_allow_html=True,
	)


def render_add_tab(exercise_names):
	"""Minimal add flow: choose workout, then append set rows."""
	st.subheader("Add Workout")

	if "add_draft_sets" not in st.session_state:
		st.session_state.add_draft_sets = []
	if "add_last_exercise" not in st.session_state:
		st.session_state.add_last_exercise = ""

	selector_options = exercise_names + ["+ Add exercise"]
	selected_workout = st.selectbox("Select workout", options=selector_options)

	if selected_workout == "+ Add exercise":
		with st.form("quick_add_exercise_form", clear_on_submit=True):
			new_exercise_name = st.text_input("New exercise name", placeholder="Push-ups")
			add_exercise_clicked = st.form_submit_button("Add exercise")
		if add_exercise_clicked:
			success, message = add_exercise(new_exercise_name)
			if success:
				st.success(message)
				st.rerun()
			st.warning(message)
		st.info("After adding, select the workout from the list.")
		return

	if not exercise_names:
		st.info("No exercises yet. Choose '+ Add exercise' to create one.")
		return

	if st.session_state.add_last_exercise != selected_workout:
		st.session_state.add_draft_sets = []
		st.session_state.add_last_exercise = selected_workout

	with st.expander("Manage exercises", expanded=False):
		with st.form("remove_exercise_form"):
			selected_to_remove = st.selectbox("Remove exercise", options=exercise_names)
			delete_history_too = st.checkbox(
				"Also delete all workout history for this exercise"
			)
			remove_clicked = st.form_submit_button("Remove exercise")
		if remove_clicked:
			success, message = remove_exercise(selected_to_remove, delete_history_too)
			if success:
				if st.session_state.add_last_exercise == selected_to_remove:
					st.session_state.add_draft_sets = []
					st.session_state.add_last_exercise = ""
				st.success(message)
				st.rerun()
			st.warning(message)

	st.markdown(f"### {selected_workout}")
	st.caption(f"Date: {date.today().isoformat()}")

	col1, col2, col3 = st.columns([1, 1, 1])
	with col1:
		reps_input = st.number_input(
			"Reps",
			min_value=0,
			max_value=2000,
			value=10,
			key="add_set_reps_input",
		)
	with col2:
		weight_input = st.number_input(
			"Weight",
			min_value=0.0,
			max_value=10000.0,
			value=0.0,
			step=0.5,
			key="add_set_weight_input",
		)
	with col3:
		st.write("")
		add_set_clicked = st.button("Add set", use_container_width=True)

	if add_set_clicked:
		st.session_state.add_draft_sets.append(
			{"Reps": int(reps_input), "Weight": float(weight_input)}
		)
		st.rerun()

	if st.session_state.add_draft_sets:
		rows = []
		for index, item in enumerate(st.session_state.add_draft_sets, start=1):
			rows.append({"Set": index, "Reps": item["Reps"], "Weight": item["Weight"]})
		st.dataframe(rows, use_container_width=True, hide_index=True)

		btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
		with btn_col1:
			remove_last_clicked = st.button("Remove last set", use_container_width=True)
		with btn_col2:
			save_workout_clicked = st.button("Save workout", use_container_width=True)
		with btn_col3:
			clear_clicked = st.button("Clear", use_container_width=True)

		if remove_last_clicked and st.session_state.add_draft_sets:
			st.session_state.add_draft_sets.pop()
			st.rerun()

		if clear_clicked:
			st.session_state.add_draft_sets = []
			st.rerun()

		if save_workout_clicked:
			reps_by_set = [item["Reps"] for item in st.session_state.add_draft_sets]
			weights_by_set = [item["Weight"] for item in st.session_state.add_draft_sets]
			add_workout_session(
				date.today().isoformat(),
				selected_workout,
				reps_by_set,
				weights_by_set,
			)
			st.session_state.add_draft_sets = []
			st.success("Workout saved.")
			st.rerun()
	else:
		st.info("Add your first set to start this workout.")


def render_edit_tab():
	"""Edit an entire session so user can change set count and reps quickly."""
	st.subheader("Edit Workout")

	sessions = get_session_choices()
	if not sessions:
		st.info("No workout sessions to edit yet.")
		return

	labels = [
		f"{session['session_date']} | {session['exercise_name']} | {session['total_sets']} sets"
		for session in sessions
	]
	selected_label = st.selectbox("Choose session", options=labels)
	selected_session = sessions[labels.index(selected_label)]

	current_sets = get_session_sets(
		selected_session["session_date"], selected_session["exercise_name"]
	)
	default_sets = max(1, len(current_sets))

	with st.form("edit_session_form"):
		# Date input field
		session_date_obj = datetime.strptime(selected_session["session_date"], "%Y-%m-%d").date()
		new_session_date = st.date_input(
			"Date",
			value=session_date_obj,
		)
		
		new_sets_count = st.number_input(
			"Sets",
			min_value=1,
			max_value=30,
			value=default_sets,
		)
		new_reps_by_set = []
		new_weights_by_set = []
		for set_index in range(int(new_sets_count)):
			default_rep = current_sets[set_index]["reps"] if set_index < len(current_sets) else 10
			default_weight = (
				current_sets[set_index]["weight"] if set_index < len(current_sets) else 0.0
			)
			col_reps, col_weight = st.columns(2)
			with col_reps:
				rep_value = st.number_input(
					f"Set {set_index + 1} reps",
					min_value=0,
					max_value=2000,
					value=int(default_rep),
					key=f"edit_reps_{set_index}",
				)
			with col_weight:
				weight_value = st.number_input(
					f"Set {set_index + 1} weight",
					min_value=0.0,
					max_value=10000.0,
					value=float(default_weight),
					step=0.5,
					key=f"edit_weight_{set_index}",
				)
			new_reps_by_set.append(int(rep_value))
			new_weights_by_set.append(float(weight_value))

		save_changes_clicked = st.form_submit_button("Save changes")
		delete_session_clicked = st.form_submit_button("Delete this session")

	if save_changes_clicked:
		new_session_date_str = new_session_date.isoformat()
		original_date_str = selected_session["session_date"]
		
		# If date has changed, delete old session and create new one
		if new_session_date_str != original_date_str:
			delete_workout_session(original_date_str, selected_session["exercise_name"])
			add_workout_session(
				new_session_date_str,
				selected_session["exercise_name"],
				new_reps_by_set,
				new_weights_by_set,
			)
		else:
			replace_workout_session(
				original_date_str,
				selected_session["exercise_name"],
				new_reps_by_set,
				new_weights_by_set,
			)
		st.success("Session updated.")
		st.rerun()

	if delete_session_clicked:
		delete_workout_session(
			selected_session["session_date"],
			selected_session["exercise_name"],
		)
		st.success("Session deleted.")
		st.rerun()


def render_history_tab(exercise_names):
	"""History tab: select exercise, then show that exercise's progress."""
	st.subheader("Workout History")

	if not exercise_names:
		st.info("No exercises yet. Add one in the Add tab first.")
		return

	selected_exercise = st.selectbox("Select exercise", options=exercise_names)

	rows = get_workout_rows(
		start_date=None,
		end_date=None,
		exercise_name=selected_exercise,
	)

	if not rows:
		st.info(f"No workouts found for {selected_exercise}.")
		return

	st.markdown(f"### {selected_exercise} Progress")

	totals = build_session_totals(rows)
	st.markdown("#### Workouts by Date")
	totals_for_display = [
		{"Date": t["Date"], "Total Reps": t["Total Reps"], "Total Sets": t["Total Sets"]}
		for t in totals
	]
	st.dataframe(totals_for_display, use_container_width=True, hide_index=True)

	points = build_progress_points(rows)
	st.markdown("#### Progress Chart")
	st.vega_lite_chart(
		{
			"$schema": "https://vega.github.io/schema/vega-lite/v5.json",
			"data": {"values": points},
			"mark": {"type": "line", "point": True, "strokeWidth": 3},
			"encoding": {
				"x": {"field": "date", "type": "temporal", "title": "Date"},
				"y": {
					"field": "total_reps",
					"type": "quantitative",
					"title": "Total reps",
				},
				"tooltip": [
					{"field": "date", "type": "temporal", "title": "Date"},
					{"field": "total_reps", "type": "quantitative", "title": "Total reps"},
				],
			},
			"width": "container",
		},
		use_container_width=True,
	)

	st.markdown("#### All Sets")
	table_rows = [
		{
			"Date": row["session_date"],
			"Set": row["set_number"],
			"Reps": row["reps_count"],
			"Weight": row["weight_used"],
		}
		for row in rows
	]
	st.dataframe(table_rows, use_container_width=True, hide_index=True)


def main():
	"""Run the Streamlit app."""
	st.set_page_config(page_title="Workout Reps Tracker", page_icon="🏋️", layout="wide")

	init_db()
	inject_styles()

	st.title("Workout Reps Tracker")
	st.markdown(
		'<p class="app-subtitle">Simple flow: add exercise once, log workouts fast, and edit full sessions later.</p>',
		unsafe_allow_html=True,
	)

	exercise_names = get_exercise_names()
	tab_add, tab_edit, tab_history = st.tabs(["Add", "Edit", "History"])

	with tab_add:
		render_add_tab(exercise_names)

	with tab_edit:
		render_edit_tab()

	with tab_history:
		render_history_tab(get_exercise_names())


if __name__ == "__main__":
	main()
