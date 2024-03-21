# univ3-coa

Uniswap v3 cost of attack calculator for TWAP oracle manipulation.

## Installation

The repo uses [ApeWorX](https://github.com/apeworx/ape) and [Silverback](https://github.com/apeworx/silverback) for development.

Set up a virtual environment

```sh
python -m venv .venv
source .venv/bin/activate
```

Install requirements and Ape plugins

```sh
pip install -r requirements.txt
ape plugins install .
```

## Usage

Run silverback


```sh
silverback run "silverback:app" --network :mainnet:alchemy --account acct-name
```
