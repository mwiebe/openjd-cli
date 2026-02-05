# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

from pathlib import Path
import re

from . import run_openjd_cli_main, format_capsys_outerr

TEMPLATE_DIR = Path(__file__).parent / "templates"


def test_run_job_with_env_default_params(capsys):
    # Run a job with env_with_param as an external environment,
    # leaving the environment's parameter at its default value

    outerr = run_openjd_cli_main(
        capsys,
        args=[
            "run",
            str(TEMPLATE_DIR / "simple_with_j_param.yaml"),
            "-p",
            "J=Jvalue",
            "--environment",
            str(TEMPLATE_DIR / "env_with_param.yaml"),
        ],
        expected_exit_code=0,
    )

    for expected_message_regex in [
        "EnvWithParam Enter DefaultForEnvParam",
        "DoTask Jvalue",
        "EnvWithParam Exit DefaultForEnvParam",
    ]:
        assert re.search(
            expected_message_regex, outerr.out
        ), f"Regex r'{expected_message_regex}' not matched in:\n{format_capsys_outerr(outerr)}"


def test_run_job_with_env_provide_env_param(capsys):
    # Run a job with env_with_param as an external environment,
    # explicitly providing the env parameter

    outerr = run_openjd_cli_main(
        capsys,
        args=[
            "run",
            str(TEMPLATE_DIR / "simple_with_j_param.yaml"),
            "-p",
            "J=Jvalue",
            "-p",
            "EnvParam=EnvParamValue",
            "--environment",
            str(TEMPLATE_DIR / "env_with_param.yaml"),
        ],
        expected_exit_code=0,
    )

    for expected_message_regex in [
        "EnvWithParam Enter EnvParamValue",
        "DoTask Jvalue",
        "EnvWithParam Exit EnvParamValue",
    ]:
        assert re.search(
            expected_message_regex, outerr.out
        ), f"Regex r'{expected_message_regex}' not matched in:\n{format_capsys_outerr(outerr)}"


def test_run_job_with_env_expr_extension(capsys, tmp_path):
    """Test that EXPR extension works in environment templates."""
    # Create a simple job template
    job_template = tmp_path / "job.yaml"
    job_template.write_text(
        """
specificationVersion: jobtemplate-2023-09
name: TestJob
extensions:
  - FEATURE_BUNDLE_1
steps:
  - name: TestStep
    bash:
      script: echo "Task ran"
"""
    )

    # Create an environment template that uses EXPR
    env_template = tmp_path / "env.yaml"
    env_template.write_text(
        """
specificationVersion: environment-2023-09
extensions:
  - EXPR
environment:
  name: ExprEnv
  script:
    actions:
      onEnter:
        command: echo
        args:
          - "Enter {{ 1 + 2 }}"
      onExit:
        command: echo
        args:
          - "Exit"
"""
    )

    outerr = run_openjd_cli_main(
        capsys,
        args=[
            "run",
            str(job_template),
            "--environment",
            str(env_template),
        ],
        expected_exit_code=0,
    )

    # The EXPR extension should evaluate 1 + 2 = 3
    assert "Enter 3" in outerr.out, f"EXPR not evaluated in env:\n{format_capsys_outerr(outerr)}"
