import subprocess
import threading
import time
from dpsdataset import source
from step.step import DPSStep
import shlex
import logging

logger = logging.getLogger(__name__)

class CustomCommandStep(DPSStep):
    def __init__(self, input_source: source, command: str, fields: list[str] | None = None,
                 execution_mode: str = "per_row", simulated: bool = True,
                 cancel_event: threading.Event | None = None):
        super().__init__(command, simulated=simulated)
        self.input_source = input_source
        self.command = command
        self.fields = fields if fields is not None else []
        self.execution_mode = execution_mode
        self.cancel_event = cancel_event

    def _is_cancelled(self) -> bool:
        return self.cancel_event is not None and self.cancel_event.is_set()

    def __run_command__(self, command: str) -> subprocess.CompletedProcess | None:
        if self.simulated:
            return subprocess.CompletedProcess(args=command, returncode=0, stdout="Simulated execution", stderr="")

        try:
            args = shlex.split(command)
            proc = subprocess.Popen(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Poll the process while checking for cancellation
            while proc.poll() is None:
                if self._is_cancelled():
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    logger.info("Command terminated due to cancellation: %s", command)
                    return None
                time.sleep(0.1)

            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                logger.error("Command failed (rc=%d): %s", proc.returncode, stderr)
                return None
            return subprocess.CompletedProcess(args=args, returncode=proc.returncode, stdout=stdout, stderr=stderr)

        except FileNotFoundError as e:
            logger.error("Command not found: %s", e)
            return None

    def execute(self) -> bool:
        sim_text = "[Simulated] " if self.simulated else ""

        if self.execution_mode != "per_row":
            logger.info("%sExecuting command once: '%s'", sim_text, self.command)
            proc = self.__run_command__(self.command)
            if proc is None:
                logger.info("Command %s.", "cancelled" if self._is_cancelled() else "failed")
                return False
            return True

        logger.info("%sExecuting command per row.", sim_text)

        for _, row in self.input_source.get_data().iterrows():
            if self._is_cancelled():
                logger.info("Execution cancelled between rows.")
                return False

            command_values = {field: None for field in self.fields}
            try:
                for field in command_values:
                    command_values[field] = row[field]
            except Exception:
                logger.error("Cannot find field '%s' in row with columns %s", field, row.index.tolist())
                return False

            final_command = self.command.format(**command_values)
            logger.info("%sExecuting: %s", sim_text, final_command)

            proc = self.__run_command__(final_command)
            if proc is None:
                if self._is_cancelled():
                    logger.info("Execution cancelled.")
                else:
                    logger.error("Command execution failed for values: %s", command_values)
                return False

        return True
