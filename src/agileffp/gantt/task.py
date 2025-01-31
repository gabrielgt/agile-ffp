from datetime import date
from agileffp.seville_calendar import Seville
from agileffp.gantt.team_task import TeamTask
from agileffp.gantt.capacity_team import CapacityTeam


class Task:
    def __init__(
        self,
        name: str,
        estimate: dict[str, int | dict[str, int]],
        depends_on: list = [],
        priority: int = 99,
    ):
        """Creates a task

        Args:
            name (str): The name of the task
            teams_effort (dict[str, int | dict[str, int]]): A dictionary with the
              effort for each team
            depends_on (list[Task], optional): A list of tasks that this task
            depends on. Defaults to None.
        """
        self.name = name
        self.depends_on = depends_on
        self.priority = priority
        self.init, self.end, self.days = None, None, None
        self.cal = Seville()

        self.teams_tasks = {
            team: TeamTask(name, team, effort) for team, effort in estimate.items()
        }

    def assign_capacity(
        self, capacity: dict[str, CapacityTeam], start_after: date = None
    ) -> None:
        """Assigns capacity to each team in the task

        Args:
            capacity (dict[str, CapacityTeam]):
            A dictionary with the capacity for each team
        """
        unavailable_teams = [k for k in self.teams_tasks.keys() if k not in capacity]
        if unavailable_teams:
            raise ValueError(
                f"Teams {unavailable_teams} don't appear on the capacity teams list"
            )

        for team, team_task in self.teams_tasks.items():
            team_task.assign_capacity(capacity[team], after=start_after)
            if self.init is None or team_task.init < self.init:
                self.init = team_task.init
            if self.end is None or team_task.end > self.end:
                self.end = team_task.end
        self.days = self.cal.get_working_days_delta(self.init, self.end) + 1

    def __str__(self):
        return f"{self.name} ({self.init} - {self.end}) - {self.days}"

    def __repr__(self):
        return str(self)

    def parse(data: dict) -> list["Task"]:
        """Parses the YAML data into Tasks

        Args:
            data (dict): The YAML data

        Returns:
            list[Task]: The tasks list
        """
        if "tasks" not in data:
            raise ValueError("Invalid YAML file")

        return [Task(**kwargs) for kwargs in data["tasks"]]
