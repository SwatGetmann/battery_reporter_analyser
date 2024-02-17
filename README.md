# Windows Battery Report Parser & Analyser

## Table of Contents

- [About](#about)
- [Usage](#usage)

## About <a name = "about"></a>

Win 10+ Battery Reports parser & analyzer.

Since Reports have only 3 last days available in a sinlge HTML page, the goal of parser is to merge the tables together in a single HTML file to get the best representation of what was happening with battery (drains/charges).

Also, the parser has a modular functionality, so that you can parse specific parts of the report.

Analyser recalculates the velocity of drains and plots charts for the merged table.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

- Python 3.12+
- BeautifulSoup 4.8.1
- Pandas (2.2+)

### Installing

A step by step series of examples that tell you how to get a development env running.

Install required libraries.

```
pip install -r ./requirements.txt
```

End with an example of getting some data out of the system or using it for a little demo.

## Usage <a name = "usage"></a>

Goes well with the PowerShell script that takes the reports: [PS Battery Reporter](https://github.com/SwatGetmann/ps_battery_reporter).

In order to run, just start main.py:

```
python main.py
```
