from .payment import payment_cli


def setup_commands(app):
    # Add your command here
    app.cli.add_command(payment_cli)
