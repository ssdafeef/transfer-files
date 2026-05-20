from flask import Flask, jsonify
from flask_cors import CORS
from ortools.linear_solver import pywraplp
import pandas as pd
import time

app = Flask(__name__)
CORS(app)

# ==========================
# LOAD DATA
# ==========================

refugees_df = pd.read_csv("synthetic_refugees_50k.csv")
cities_df = pd.read_csv("synthetic_cities_50.csv")

cities_df["job_demand"] = cities_df["job_demand"].apply(lambda x: x.split(","))

# ==========================
# AGGREGATE REFUGEES
# ==========================

group_columns = [
    "primary_language",
    "skill_type",
    "education_level",
    "preferred_cost_level"
]

grouped = refugees_df.groupby(group_columns).agg({
    "refugee_id": "count",
    "family_size": "mean",
    "trauma_level": "mean",
    "adaptability_index": "mean"
}).reset_index()

grouped = grouped.rename(columns={"refugee_id": "group_size"})

print("Grouped clusters:", len(grouped))

# ==========================
# SCORE FUNCTION
# ==========================

def compute_score(group, city):
    score = 0

    if group["primary_language"] == city["primary_language"]:
        score += 0.25

    if group["skill_type"] in city["job_demand"]:
        score += 0.25

    edu_weights = {
        "None": 0.0,
        "Primary": 0.05,
        "Secondary": 0.1,
        "Bachelor": 0.15,
        "Master": 0.2
    }

    score += edu_weights.get(group["education_level"], 0)

    if group["preferred_cost_level"] == city["cost_level"]:
        score += 0.1

    score += (1 - float(city["unemployment_rate"])) * 0.1
    score += float(group["adaptability_index"]) * 0.05
    score -= float(group["trauma_level"]) * 0.01

    return max(score, 0)

# ==========================
# OPTIMIZATION ROUTE
# ==========================

@app.route("/optimize", methods=["GET"])
def optimize():

    start = time.time()

    solver = pywraplp.Solver.CreateSolver("CBC")
    solver.SetTimeLimit(180000)

    num_groups = len(grouped)
    num_cities = len(cities_df)

    x = {}

    for i in range(num_groups):
        for j in range(num_cities):
            x[(i, j)] = solver.NumVar(
                0,
                float(grouped.loc[i, "group_size"]),
                f"x_{i}_{j}"
            )

    solver.Maximize(
        solver.Sum(
            compute_score(grouped.loc[i], cities_df.loc[j]) * x[(i, j)]
            for i in range(num_groups)
            for j in range(num_cities)
        )
    )

    # Assign up to group size
    for i in range(num_groups):
        solver.Add(
            solver.Sum(x[(i, j)] for j in range(num_cities))
            <= float(grouped.loc[i, "group_size"])
        )

    # Capacity constraint
    for j in range(num_cities):
        solver.Add(
            solver.Sum(
                float(grouped.loc[i, "family_size"]) * x[(i, j)]
                for i in range(num_groups)
            )
            <= float(cities_df.loc[j, "capacity"])
        )

    status = solver.Solve()

    solve_time = solver.WallTime()

    total_allocated = 0
    allocations = []

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        total_score = solver.Objective().Value()

        for j in range(num_cities):
            allocated = sum(
                x[(i, j)].solution_value()
                for i in range(num_groups)
            )

            total_allocated += allocated

            allocations.append({
                "city": cities_df.loc[j, "city_name"],
                "allocated_refugees": int(round(allocated)),
                "capacity": int(cities_df.loc[j, "capacity"])
            })
    else:
        total_score = 0

    end = time.time()

    return jsonify({
        "original_refugees": int(len(refugees_df)),
        "grouped_clusters": int(num_groups),
        "cities": int(num_cities),
        "objective_value": round(total_score, 2),
        "total_allocated_refugees": int(round(total_allocated)),
        "unallocated_refugees": int(len(refugees_df) - round(total_allocated)),
        "solve_time_ms": int(solve_time),
        "runtime_seconds": round(end - start, 2),
        "city_allocations": allocations
    })


if __name__ == "__main__":
    app.run(debug=True)