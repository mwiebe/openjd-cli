# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

from enum import Enum

from typing import Any, Optional

from openjd.model import Step, TaskParameterSet
from openjd.model import Environment
from openjd.sessions import Session


class EnvironmentType(str, Enum):
    """
    The three different types of environment types that can be entered/exited in a session.
    """

    EXTERNAL = "EXTERNAL"
    JOB = "JOB"
    STEP = "STEP"
    ALL = "ALL"

    def matches(self, other: "EnvironmentType") -> bool:
        """Environment types match if they are equal, or one of them is ALL."""
        return self == other or self == EnvironmentType.ALL or other == EnvironmentType.ALL


class SessionAction:
    _session: Session
    duration: float

    def __init__(self, session: Session):
        self._session = session

    def run(self):
        """
        Subclasses of `SessionAction` should have
        custom implementations of this depending on their type.
        """


class RunTaskAction(SessionAction):
    _step: Step
    _parameters: TaskParameterSet

    def __init__(self, session: Session, step: Step, parameters: TaskParameterSet):
        super(RunTaskAction, self).__init__(session)
        self._step = step
        self._parameters = parameters

    def run(self):
        self._session.run_task(
            step_script=self._step.script,
            task_parameter_values=self._parameters,
            resolved_bindings=self._step.resolvedBindings,
        )

    def __str__(self):
        parameters = {name: parameter.value for name, parameter in self._parameters.items()}
        return f"Run Step '{self._step.name}' with Task parameters '{str(parameters)}'"


class EnterEnvironmentAction(SessionAction):
    _environment: Environment
    _id: str
    _resolved_bindings: Optional[list[dict[str, Any]]]

    def __init__(
        self,
        session: Session,
        environment: Environment,
        env_id: str,
        resolved_bindings: Optional[list[dict[str, Any]]] = None,
    ):
        super(EnterEnvironmentAction, self).__init__(session)
        self._environment = environment
        self._id = env_id
        self._resolved_bindings = resolved_bindings

    def run(self):
        self._session.enter_environment(
            environment=self._environment,
            identifier=self._id,
            resolved_bindings=self._resolved_bindings,
        )

    def __str__(self):
        return f"Enter Environment '{self._environment.name}'"


class ExitEnvironmentAction(SessionAction):
    _id: str
    _keep_session_running: bool
    _resolved_bindings: Optional[list[dict[str, Any]]]

    def __init__(
        self,
        session: Session,
        id: str,
        keep_session_running: bool,
        resolved_bindings: Optional[list[dict[str, Any]]] = None,
    ):
        super(ExitEnvironmentAction, self).__init__(session)
        self._id = id
        self._keep_session_running = keep_session_running
        self._resolved_bindings = resolved_bindings

    def run(self):
        self._session.exit_environment(
            identifier=self._id,
            keep_session_running=self._keep_session_running,
            resolved_bindings=self._resolved_bindings,
        )

    def __str__(self):
        return f"Exit Environment '{self._id}'"
