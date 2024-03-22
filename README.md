# univ3-coa

[Uniswap v3](https://github.com/uniswap/v3-core) cost of attack calculator for TWAP oracle manipulation.

## Installation

The repo uses [ApeWorX](https://github.com/apeworx/ape) for development.

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

Run the [`populate.py`](scripts/populate.py) script to gather liquidity profile data from a specified Uniswap v3 pool

```sh
ape run populate
INFO: Starting 'anvil' process.
Running populate.py on chainid 1 at block number 19486609 ...
Uniswap v3 pool address: 0x11950d141EcB863F01007AdD7D1A342041227b58
Pool tick spacing: 60
Pool slot0.tick: -198946
Pool liquidity: 67967809990478318242330008
Start tick: -198900
Max oracle tick delta: 50
Max tick delta: 180000
Stop ticks (down, up): (-378901, -18899)
Up toward tick max: False
Querying liquidity net values for pool tick range ...
Tick info liquidity net at tick -198900: 0
Tick info liquidity net at tick -198960: -1653259127695897829718756
```

Then run the [`calculate.py`](scripts/calculate.py) script to determine cost of attack figures given the gathered liquidity profile

```sh
ape run calculate
INFO: Starting 'anvil' process.
Running calculate.py on chainid 1 at block number 19489746 ...
Uniswap v3 pool address: 0x11950d141EcB863F01007AdD7D1A342041227b58
Token0 0x6982508145454Ce325dDbE47a25d4ec3d2311933 has decimals: 18
Token1 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 has decimals: 18
Pool fee: 3000
Populated Uniswap v3 pool ticks filepath: scripts/results/0x11950d141EcB863F01007AdD7D1A342041227b58_19486609_-198900_-378901.csv
Populated Uniswap v3 pool ticks:         tick               liquidity_net                   liquidity
0    -198900                           0  67967809990478318242330008
1    -198960  -1653259127695897829718756  69621069118174216072048764
2    -199020                           0  69621069118174216072048764
3    -199080   1453383616684516494893673  68167685501489699577155091
4    -199140                           0  68167685501489699577155091
...      ...                         ...                         ...
2996 -378660                           0    608066211499668570996838
2997 -378720                           0    608066211499668570996838
2998 -378780                           0    608066211499668570996838
2999 -378840                           0    608066211499668570996838
3000 -378900                           0    608066211499668570996838

[3001 rows x 3 columns]
```
