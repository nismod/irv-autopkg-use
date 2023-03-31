# irv-autopkg-use

A project exemplifying the `irv-autopkg-client` API.

## Background

The irv-autopkg service allows users to extract portions of global datasets
pertaining to climate risk and resilience. The `irv-autopkg-client` Python
package is a client API for interacting with the irv-autopkg service.

## Introduction

This repository consists of several Python notebooks and some supporting
modules. The notebooks demonstrate querying the API for available datasets and
boundaries. Subsequently, some datasets are visualised and a simple risk
calculation performed.

## Installation

First, clone this repository:

```
git clone git@github.com:nismod/irv-autopkg-use.git
```

To install this project, it is recommended to use the conda environment manager
to create an appropriate Python environment. This should install all the
necessary dependencies:

```
conda env create --file environment.yml
```

## Usage

To use the notebooks, first activate the Python environment:

```
conda activate irv-autopkg
```

Then, from the directory containing this README.md, start a notebook server:

```
jupyter notebook
```

And a browser tab should open listing the notebook (.ipynb) files.

Have a read through the first one for examples of how to use the API.
Subsequent notebooks demonstrate using downloaded data.

## Next steps

Modify the notebooks as you require, or use them as inspiration for writing
your own scripts.
