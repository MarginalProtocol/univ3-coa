import click
import pandas as pd

from ape import chain, Contract, networks

MIN_TICK = -887272
MAX_TICK = -MIN_TICK

SECONDS_AGO = 43200
BLOCK_TIME = 12


def main():
    block = chain.blocks.head
    ecosystem = networks.provider.network.ecosystem.name
    click.echo(
        f"Running populate.py on chainid {chain.chain_id} at block number {block.number} ..."
    )

    pool_address = click.prompt("Uniswap v3 pool address", type=str)
    pool = Contract(pool_address)

    tick_spacing = pool.tickSpacing()
    click.echo(f"Pool tick spacing: {tick_spacing}")

    slot0 = pool.slot0()
    click.echo(f"Pool slot0.tick: {slot0.tick}")

    liquidity = pool.liquidity()
    click.echo(f"Pool liquidity: {liquidity}")

    start_tick = (
        slot0.tick - slot0.tick % tick_spacing
        if slot0.tick >= 0
        else -(-slot0.tick - (-slot0.tick) % tick_spacing)
    )
    click.echo(f"Start tick: {start_tick}")

    # max manipulation on time weighted average tick translates moving to max tick delta in spot
    max_oracle_tick_delta = click.prompt("Max oracle tick delta", type=int)
    max_tick_delta = (max_oracle_tick_delta * SECONDS_AGO) // BLOCK_TIME
    click.echo(f"Max tick delta: {max_tick_delta}")

    stop_tick_up = start_tick + max_tick_delta + 1
    stop_tick_down = start_tick - max_tick_delta - 1
    click.echo(f"Stop ticks (down, up): {(stop_tick_down, stop_tick_up)}")

    up = click.prompt("Up toward tick max", type=bool)
    r = (
        range(start_tick, stop_tick_up, tick_spacing)
        if up
        else range(start_tick, stop_tick_down, -tick_spacing)
    )
    tick_range = [tick for tick in r]
    stop_tick = stop_tick_up if up else stop_tick_down

    click.echo("Querying liquidity net values for pool tick range ...")
    liquidity_net = []
    for tick in tick_range:
        tick_info = pool.ticks(tick)
        click.echo(f"Tick info liquidity net at tick {tick}: {tick_info.liquidityNet}")
        liquidity_net.append(tick_info.liquidityNet)

    df = pd.DataFrame(
        data={
            "tick": tick_range,
            "liquidity_net": liquidity_net,
        }
    )
    df["liquidity"] = (
        liquidity + df["liquidity_net"].cumsum()
        if up
        else liquidity - df["liquidity_net"].cumsum()
    )
    click.echo(f"Uniswap v3 pool liquidity profile: {df}")

    click.echo(f"Saving pool liquidity profile for pool {pool_address} ...")
    df.to_csv(
        f"scripts/results/{ecosystem}/{pool_address}_{block.number}_{start_tick}_{stop_tick}.csv",
        index=False,
    )
