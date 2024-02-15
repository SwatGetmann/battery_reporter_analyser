# Windows Battery Report Parser & Analyser

## Table of Contents

- [About](#about)
- [Usage](#usage)

## About <a name = "about"></a>

Win 10+ Battery Reports parser & analyzer.

Since Reports have only 3 last days available in a sinlge HTML page, the goal of parser is to merge the tables together in a single HTML file to get the best representation of what was happening with battery (drains/charges).

Also, the parser has a modular functionality, so that you can parse specific parts of the report.

Analyser recalculates the velocity of drains and plots charts for the merged table.

## Usage <a name = "usage"></a>

Goes well with the PowerShell script that takes the reports: [PS Battery Reporter](https://github.com/SwatGetmann/ps_battery_reporter).

Add notes about how to use the system.
