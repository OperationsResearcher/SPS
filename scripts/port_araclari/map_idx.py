# -*- coding: utf-8 -*-
import json, sys
sp = sys.argv[1]
Y = json.load(open(sp + "/yeni_msgid.json", encoding="utf-8"))
E = {
19: "Account, profile, organization and system configuration",
37: "K-Report — Corporate Reporting Center",
38: "Strategy · Process · KPI · Activity · Risk · Data Quality · 360° report view in 23 tabs ·",
39: "RPN (Risk Priority Number)",
40: "= Likelihood × Impact (between 1–5).",
41: "High ≥8", 42: "Medium/Low <8",
43: "— Filtered by the selected plan year.",
44: "Level:", 45: "= Optimized |", 46: "= Initial",
47: "Last 90 days", 48: "Last 180 days", 49: "Alert Center",
50: "— Three alert categories requiring immediate action in the selected year:",
51: "① Critical KPI", 52: "achievement <%%50 ·", 53: "② High Risk", 55: "③ Overdue Activity", 56: "past due date",
57: "What is EVM (Earned Value Management)?",
58: "A project's", 59: "plan, progress and cost",
60: "data combined into a single metric — the PMI standard method. Instead of \"We spent this much budget\", it answers the question \"",
61: "how much of the targeted work was completed for the budget we spent?",
62: "\".",
67: "ahead of / on schedule", 68: "slight delay · monitor", 69: "behind schedule · action",
71: "under budget / efficient", 72: "slight overrun · monitor", 73: "over budget · action",
74: "How to interpret result combinations?",
75: "Schedule Performance Index = EV/PV", 76: "Cost Performance Index = EV/AC",
77: "GitHub-style heat map", 78: "KPI coverage pie chart", 79: "Strategy alignment pie chart",
80: "Process operations bar chart", 81: "Process risk bar chart", 82: "KPI score distribution",
83: "Project completion status pie chart", 84: "Task distribution pie chart", 85: "Project risk bar chart",
86: "Enrich with AI",
94: "CMMI Maturity Heat Map — Kokpitim", 95: "CMMI Maturity Heat Map",
96: "Strategic Flow Map — Kokpitim", 97: "K-Vector Skew — Kokpitim", 98: "K-Vector Skew Report",
99: "ML Anomaly Detection — Kokpitim", 100: "ML Anomaly Detection",
104: "AI Sector Benchmark — Kokpitim", 105: "Data Quality — Kokpitim", 106: "Data Quality Report",
107: "Head Office updated", 108: "Target and actual values are unchanged. No approval needed.",
118: "Head Office updated — Kokpitim",
119: "The core definition was written to the branch. Target and actual values are unchanged. No approval.",
120: "This list is for the branch.", 121: "There are no core updates written to your branch.",
}
M = {Y[i][0]: v for i, v in E.items()}
json.dump(M, open(sp + "/map.json", "w", encoding="utf-8"), ensure_ascii=False)
Y2 = [y for y in Y if y[0] in M]
json.dump(Y2, open(sp + "/yeni_msgid.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(M), len(Y2))
