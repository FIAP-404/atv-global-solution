# Project Brief: Space Mission Monitoring System

## Overview

This Global Solution project challenges students to build a software solution for a realistic problem in the modern space industry. The main theme is the use of intelligent monitoring, control, data analysis, and decision-support systems in space missions.

The project should simulate a basic operational monitoring system for an experimental space mission. The system must receive or define simulated telemetry data, interpret the mission state, identify risks, generate automatic alerts, estimate the behavior of at least one critical variable, and recommend technical actions to keep the operation safe.

The solution does not need a graphical interface. A terminal-based Python program is enough, as long as it is functional, well organized, documented, and clearly demonstrates the required programming concepts.

## Project Period and Format

- Project period: May 25, 2026 to June 9, 2026.
- Format: individual work or groups of up to 5 students.
- Final submission: a `.txt` file submitted through FIAP ON containing only:
  - the public GitHub repository link;
  - the unlisted YouTube presentation video link.

## Main Objective

Develop an intelligent monitoring system for basic control of an experimental space mission.

The system must apply programming, algorithms, computational thinking, and simple artificial intelligence concepts to:

- interpret operational data;
- classify the mission state as normal, alert, or critical;
- generate automatic alerts;
- analyze critical situations;
- provide technical recommendations.

## Required Mission Scenario

The project should represent a realistic space operation scenario. The mission may involve topics such as:

- survival outside Earth;
- energy management;
- life support;
- communication between planets or remote stations;
- autonomous monitoring;
- sustainability;
- aerospace safety;
- habitat or laboratory operation.

The system must handle incomplete, inconsistent, or risky data clearly enough to justify its diagnosis and recommendations.

## Required Simulated Data

The project must include a minimum telemetry dataset. The data may be read from an external file, such as CSV, JSON, or TXT, or embedded directly in the code. If embedded, the repository should still include a placeholder data file.

The simulated telemetry must include:

- binary status values for at least 6 critical modules;
- energy generation and consumption readings for at least 6 different times;
- energy reserve values;
- environmental variables, such as temperature, radiation level, communication quality, or wind speed;
- an event log with at least 8 records;
- at least one intentional inconsistency to test diagnostic capability.

Example critical modules:

- life support;
- energy;
- communication;
- habitat;
- laboratory;
- storage.

Example event log entries:

- alerts;
- system restarts;
- sensor failures;
- priority changes;
- energy-saving mode activation.

## Data Interpretation Requirements

The system must clearly define which data represents the mission state.

It must:

- use boolean variables or `0`/`1` values for critical module status;
- create a simple status table showing whether modules are normal, in alert, or critical;
- include at least one interpretation rule based on numeric systems, binary states, or safety ranges.

## Data Structure Requirements

The solution must demonstrate practical use of fundamental data structures.

It must use:

- lists for time-series data, such as energy generation, consumption, reserve, or temperature;
- a queue for pending alerts, organized by arrival order or priority;
- a stack for recently analyzed critical events;
- dictionaries or hash tables for fast access to module data by name;
- a hierarchy to represent mission areas, such as energy, habitat, communication, or life support;
- a matrix or list of lists to represent readings by time and variable.

## Logical Rules Requirements

The system must implement decision rules that classify the operational state of the mission.

It must:

- use `if`, `elif`, and `else`;
- use logical operators `and`, `or`, and `not` in at least three distinct rules;
- include the main boolean diagnostic expression in the README;
- explain in plain language why each rule generates a diagnosis or action.

The mission status should be classified as:

- normal;
- alert;
- critical.

## Automatic Alert Requirements

The system must generate automatic alerts for critical or anomalous conditions.

Alerts should cover situations such as:

- failure of essential modules;
- low energy reserve;
- compromised communication;
- unsafe environmental readings;
- inconsistent telemetry.

Each alert must include:

- severity level: normal, alert, or critical;
- clear description;
- recommended action.

Alerts must be displayed clearly and organized so the most critical issues are easy to identify.

## Analysis and Forecasting Requirements

The project must apply a simple analysis or forecasting technique without relying on advanced libraries.

Acceptable techniques include:

- linear regression;
- moving average;
- trend extrapolation.

Possible variables for analysis:

- available energy;
- energy consumption;
- renewable energy generation;
- temperature;
- communication quality.

The forecast must show:

- the data used;
- the method applied;
- the predicted result;
- how the prediction affects at least one system recommendation or decision.

## Expected Example Behavior

The project may follow a flow similar to this:

Input scenario:

- energy reserve: `32%`;
- consumption: `78 kWh`;
- solar generation: `25 kWh`;
- life support: `1`;
- communication: `0`;
- radiation: high.

Expected diagnosis:

- critical alert due to low energy, unstable communication, and high radiation.

Expected forecast:

- if consumption continues at the same pace, energy reserve may fall to `24%` in the next cycle.

Expected recommendations:

- keep life support and emergency communication active;
- shut down laboratory and non-essential systems;
- redirect energy to habitat and battery charging.

## Required Repository Structure

The GitHub repository must contain exactly the required files and folders:

```text
README.md
src/sistema.py
data/dados.csv or data/dados.txt
docs/relatorio.pdf
docs/link_video.txt
docs/uso_ia.md optional
```

### README.md

The README must include:

- team name and student RMs;
- problem summary and analyzed scenario;
- data structures used and why;
- main logical diagnostic rules;
- forecasting technique and result;
- execution instructions: `python src/sistema.py`;
- example input and output;
- generated recommendations;
- YouTube video link;
- conclusions and lessons learned.

### src/sistema.py

This file must contain the complete Python system.

It must:

- run without errors;
- be functional;
- be commented where useful;
- use functions, loops, conditionals, lists, dictionaries, queues, stacks, matrices, and clear logic.

### data/dados.csv or data/dados.txt

This file must contain the simulated telemetry data.

If data is embedded directly in the code, this file may be empty as a placeholder, but the data must still be clearly documented.

### docs/relatorio.pdf

The report must have 4 to 8 pages and explain:

- the analysis;
- the data structures;
- the logical rules;
- the forecasting method;
- the technical decisions.

### docs/link_video.txt

This file must contain the exact unlisted YouTube video link.

### docs/uso_ia.md

This file is optional. If artificial intelligence was used, it must explain:

- how AI was used;
- which parts it supported;
- what critical validation the team performed.

If AI was not used, this file may be omitted.

## Technical Rules

The project should prioritize fundamental Python programming concepts from the first three course phases.

Recommended concepts:

- variables;
- conditionals;
- loops;
- functions;
- lists;
- dictionaries;
- files;
- queues;
- stacks;
- matrices;
- boolean logic;
- simple mathematical analysis.

Libraries such as Pandas, NumPy, Scikit-learn, Streamlit, or web frameworks are allowed, but the project must still preserve the students' own computational logic, data interpretation, and analysis.

The forecasting logic must clearly demonstrate the reasoning used in the implementation.

## Evaluation Rubric

The project is worth 10 points.

| Criterion | Points | What will be evaluated |
| --- | ---: | --- |
| Data interpretation | 1.0 | Clear problem definition, coherent data, identified anomalies and risks |
| Data structures | 1.5 | Correct use and justification of lists, queues, stacks, dictionaries, hierarchies, and matrices |
| Logic and rules | 1.5 | Use of `if`/`elif`/`else`, `and`/`or`/`not`, clear boolean expression, justified decisions |
| Analysis and forecasting | 1.5 | Simple technique implemented, data shown, result interpreted, decision influenced |
| Python code | 2.0 | Functional, organized, commented, compatible with course phase 3 |
| Presentation video | 2.0 | Clear explanation, live system execution, diagnosis explained, decisions defended, up to 4 minutes |
| Documentation and organization | 0.5 | Clear README, organized files, functional links, easy execution |

## Delivery Checklist

- Public GitHub repository is accessible.
- Submitted `.txt` file contains the correct repository and video links.
- YouTube video is published as unlisted.
- Python code runs without errors.
- Example input and output are documented.
- Data structures are varied and justified.
- Forecasting technique is implemented.
- Automatic alerts work.
- Recommendations are prioritized.
- `docs/uso_ia.md` is completed if AI was used.

## Important Success Criteria

The final project should prove that the team can:

- understand a realistic operational problem;
- organize data efficiently;
- apply logical decision rules;
- detect risk conditions;
- forecast a critical variable;
- transform data into useful technical recommendations;
- explain and defend technical decisions clearly.

The goal is not only to deliver working code, but to show understanding of the problem, the data, the logic, and the operational impact of the system's recommendations.
