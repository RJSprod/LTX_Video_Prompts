def timing(seconds: float) -> str:
    if seconds <= 5:
        return f"Plan a single readable action arc across {seconds:g} seconds: establish, perform, settle."
    first = round(seconds * .25, 1); middle = round(seconds * .75, 1)
    return f"Shot timing: 0-{first:g}s establish subject and space; {first:g}-{middle:g}s develop the primary action; {middle:g}-{seconds:g}s resolve naturally."
