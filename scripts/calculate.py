import click
import numpy as np
import pandas as pd

from ape import chain, Contract


def calc_sqrt_price_x96_from_tick(tick: int) -> int:
    return int(np.sqrt(1.0001**tick) * (1 << 96))


def calc_delta_reserves(
    liquidity: int, sqrt_price_x96_start: int, sqrt_price_x96_end: int
) -> (int, int):
    dx = (liquidity * (1 << 96)) // sqrt_price_x96_end - (
        liquidity * (1 << 96)
    ) // sqrt_price_x96_start
    dy = (liquidity * (sqrt_price_x96_end - sqrt_price_x96_start)) // (1 << 96)
    return (dx, dy)


def main():
    block = chain.blocks.head
    click.echo(
        f"Running calculate.py on chainid {chain.chain_id} at block number {block.number} ..."
    )

    pool_address = click.prompt("Uniswap v3 pool address", type=str)
    pool = Contract(pool_address)

    token0 = Contract(pool.token0())
    token1 = Contract(pool.token1())

    decimals0 = token0.decimals()
    decimals1 = token1.decimals()
    click.echo(f"Token0 {token0.address} has decimals: {decimals0}")
    click.echo(f"Token1 {token1.address} has decimals: {decimals1}")

    fee = pool.fee()
    click.echo(f"Pool fee: {fee}")

    path = click.prompt("Populated Uniswap v3 pool ticks filepath", type=str)
    df = pd.read_csv(path)
    click.echo(f"Populated Uniswap v3 pool ticks: {df}")

    # up if last tick > initial tick
    up = df["tick"].iloc[-1] > df["tick"].iloc[0]
    click.echo(f"Up to tick max?: {up}")

    # infer tick spacing
    tick_spacing = (
        df["tick"].iloc[1] - df["tick"].iloc[0]
        if up
        else df["tick"].iloc[0] - df["tick"].iloc[1]
    )
    click.echo(f"Tick spacing: {tick_spacing}")

    df["sqrtPriceX96"] = df["tick"].apply(calc_sqrt_price_x96_from_tick)
    df["sqrtPriceX96Next"] = df["sqrtPriceX96"].shift(
        periods=-1, fill_value=df["sqrtPriceX96"].iloc[-1]
    )

    df["dx"] = df.apply(
        lambda e: calc_delta_reserves(
            int(e.liquidity), int(e.sqrtPriceX96), int(e.sqrtPriceX96Next)
        )[0],
        axis=1,
    )
    df["dy"] = df.apply(
        lambda e: calc_delta_reserves(
            int(e.liquidity), int(e.sqrtPriceX96), int(e.sqrtPriceX96Next)
        )[1],
        axis=1,
    )

    # convert to float for pandas calculations to avoid overflow with large ints
    df["dx_float"] = df["dx"] / (10**decimals0)
    df["dy_float"] = df["dy"] / (10**decimals1)

    # total capital to move up to next tick is cumulative some of dx, dy
    df["x_float"] = df["dx_float"].cumsum()
    df["y_float"] = df["dy_float"].cumsum()

    # fees lost on single leg of swap
    df["fees_x_float"] = df["x_float"].apply(lambda x: (x * fee) / 1e6 if x > 0 else 0)
    df["fees_y_float"] = df["y_float"].apply(lambda x: (x * fee) / 1e6 if x > 0 else 0)

    click.echo(f"Populated Uniswap v3 pool ticks with calculated reserve deltas: {df}")
    new_path = path[: -len(".csv")] + "_with-calculations.csv"
    df.to_csv(new_path, index=False)
