# Improved-Restaurant-Management-System

I tried to create a nice-looking window using tkinter and especially ttk. I get ride of the classic and ugly default window. I recreated the menu bar, the fullscreen feature and the minimisation of the window in the OS task bar.

## Requirements

* Python 3.6 or higher (Developped on Windows, warn me if you encounter troubles on OsX/Linux)
* `pip install - r requirements.txt`

## Usefull features for other projects

| Advanced Feature      | Code Implementation    | Documentation or StackOverflow issue|
| :-------------        | :----------:           | -----------: |
| ToolTip widget        | [tooltip.py](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/tooltip.py) | [Source](https://stackoverflow.com/questions/3221956#answer-36221216)   |
| Creating pdf document from nothing | [save_bill_to_pdf](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/restaurant_app.py#L480)          | [Doc](https://www.reportlab.com/docs/reportlab-userguide.pdf) |
| Allow the window to be dragged | [Bind movements](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/restaurant_app.py#L111) | [Source](https://stackoverflow.com/questions/4055267#answer-4055612)   |
| Scientific calculator for raw string | [scient_calc.py](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/scient_calc.py) | Parse input string and calculate it '5+5*5'|
| Deeply customize style | [Improved ttk themes](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/restaurant_app.py#L151) | Map styles for design and events |
| Allow iconification of a custom window | [Setting](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/restaurant_app.py#L523) & [Feature](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/restaurant_app.py#L529) | (Can't find stack origin) |
| Reorganize all widget coordinates according to the window size | [place_widgets](https://github.com/s-rigaud/Improved-Restaurant-Management-System/blob/master/app/restaurant_app.py#L549) | Use the ratio between old and new window size |

## Overview of the app

#### PRICE CALCULATION + CALCULATOR

![Fisrt tab](https://github.com/s-rigaud/Improved-Restaurant-Management-System/raw/master/front.png)
![Second tab](https://github.com/s-rigaud/Improved-Restaurant-Management-System/raw/master/back.png)

#### PDF BILL

![PDF Bill](https://github.com/s-rigaud/Improved-Restaurant-Management-System/raw/master/bill.png)
