
import click
import logging
import re
from spd3303x import SPD3303X

logger = logging.getLogger("spd3303x")

@click.group(context_settings=dict(help_option_names=["-h", "--help"], obj={}))
@click.option("-v", "--verbose", count=True, default=2)
@click.option("-d", "--device", type=str)
@click.pass_context
def cli(ctx, verbose, device):


    if verbose == 0:
        logger.setLevel(logging.ERROR)
    elif verbose == 1:
        logger.setLevel(logging.WARNING)
    elif verbose == 2:
        logger.setLevel(logging.INFO)
    elif verbose > 2:
        logger.setLevel(logging.DEBUG)

    ctx.obj["verbose"] = verbose

    if device is None:
        logger.info("No device specified. Trying USB.")
        ctx.obj["device"] = SPD3303X.usb_device()
    else:
        if re.match("USB\d?::.*", device) is None:
            logger.debug(f"Assuming Ethernet device at {device}")
            ctx.obj["device"] = SPD3303X.ethernet_device(device)
        else:
            logger.debug(f"Assuming USB device at {device}")
            ctx.obj["device"] = SPD3303X.usb_device(device)


@cli.command(short_help="Set channel")
@click.argument("channel", type=int)
@click.option("--voltage", "-v", type=float, help="Voltage")
@click.option("--current", "-c", type=float, help="Current")
@click.option("--on/--off", default=False, help="Current")
@click.pass_context
def set(ctx, channel, voltage, current, on):
    with ctx.obj["device"] as dev:
        channel_name = f"CH{channel}"
        channel = getattr(dev, channel_name)
        channel.set_output(False)
        if voltage is not None:
            try:
                channel.set_voltage(voltage)
            except AttributeError:
                raise click.UsageError(f"{channel_name} does not support setting voltage")

        if current is not None:
            try:
                channel.set_current(current)
            except AttributeError:
                raise click.UsageError(f"{channel_name} does not support setting current")
        channel.set_output(on)
