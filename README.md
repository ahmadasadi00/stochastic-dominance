# Stochastic Dominance Calculator

The Stochastic Dominance Calculator is a Python-based project that implements the Babbel and Herce algorithm for calculating dominance between asset returns. This algorithm is particularly useful for comparing the performance of different assets or strategies.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Usage](#usage)

## Introduction

Stochastic dominance is a concept widely used in finance to compare the risk-return profiles of different investments. The Babbel and Herce algorithm, as described in "A Closer Look at Stable Value Funds Performance," provides a method to quantify the dominance relationship between asset returns or strategy returns. I implented First Order, Second Order and Third Order stochastic dominance. For more information please visit: [Stochastic Dominance Wikipedia](https://en.wikipedia.org/wiki/Stochastic_dominance)

The link to the paper: [A Closer Look at Stable Value Funds Performance](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1021361)

## Features

- Calculate 1st, 2nd and 3rd order stochastic dominance between asset returns.
- Compare the performance of different assets or strategies.
- Easy-to-use Python API for integrating the dominance calculation into your own projects.

## Folder Structure

stochastic-dominance/  
├── data/  
│ ├── asset_return_1.csv   
│ ├── asset_return_2.csv  
│ ├── strategy_return_1.csv  
│ ├── strategy_return_2.csv  
│ └── ...  
├── dominance/  
│ ├── dominance.py  
├── utils/  
│ ├── prepare_data.py  
│ ├── progress_bar.py  
├── simple_run.ipynb  
├── backtest.ipynb


- **data**: Contains CSV files of asset returns or strategy returns. Strategy returns refer to the returns of backtested or live-tested strategies.
- **dominance**: Contains the main implementation of the dominance calculator algorithm.
- **utils**: Contains utility functions and helper modules.

## Installation

Clone the repository:

```bash
git clone https://github.com/ahmadasadi00/stochastic-dominance.git
```

## Usage

For usage, I provided two Jupyter Notebooks with comprehensive comments and explanations of how to use this repo