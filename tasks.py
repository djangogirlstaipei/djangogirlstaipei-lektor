from __future__ import unicode_literals

import os
import shutil

import invoke
import six

from lektor.builder import Builder
from lektor.cli import Context
from lektor.devserver import run_server
from lektor.reporter import CliReporter, reporter

if six.PY2:
    input = raw_input   # noqa


ROOT_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(ROOT_DIR, 'build')


@invoke.task()
def serve(ctx):
    lektor_cli_ctx = Context()
    lektor_cli_ctx.load_plugins()

    env = lektor_cli_ctx.get_env()
    run_server(
        ('127.0.0.1', 5000), env=env, output_path=OUTPUT_DIR, verbosity=0,
    )


@invoke.task()
def remove(ctx, relpath):
    lektor_cli_ctx = Context()
    lektor_cli_ctx.load_plugins()

    env = lektor_cli_ctx.get_env()
    path = os.path.join(OUTPUT_DIR, relpath)
    with CliReporter(env, verbosity=0), reporter.build('prune', None):
        if os.path.exists(path):
            reporter.report_pruned_artifact(relpath)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


@invoke.task()
def build(ctx):
    lektor_cli_ctx = Context()
    lektor_cli_ctx.load_plugins()

    env = lektor_cli_ctx.get_env()
    pad = env.new_pad()

    # This is essentially `lektor build --output-path build`.
    with CliReporter(env, verbosity=0):
        builder = Builder(pad, OUTPUT_DIR)
        failures = builder.build_all()

    if failures:
        raise invoke.Exit('Builder failed.')
