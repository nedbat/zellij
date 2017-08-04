"""Command-line interface for Zellij."""

import click

_common_options = {
    'drawing': [
        click.option('--output', default='drawing.png', help='File name to write to'),
        click.option('--tiles', default=4, help='How many tiles to fit in the drawing'),
        click.option('--size', default='dsize'),
        click.option('--format', default='png'),
        click.argument('design'),
    ],
}

def common_options(category):
    def _wrapper(func):
        # from: https://github.com/pallets/click/issues/108#issuecomment-194465429
        for option in reversed(_common_options[category]):
            func = option(func)
        return func
    return _wrapper

@click.group()
def main():
    pass

@main.command()
@common_options('drawing')
def one(**kwargs):
    print(kwargs)
    print('one')

@main.command()
@common_options('drawing')
def two(**kwargs):
    print(kwargs)
    print('two')
