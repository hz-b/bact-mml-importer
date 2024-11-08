from dataclasses import dataclass


@dataclass(frozen=True)
class SurveyInformation:
    longitudinal_position: float
