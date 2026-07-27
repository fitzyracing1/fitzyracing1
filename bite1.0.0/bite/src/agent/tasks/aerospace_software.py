from .base import SearchTarget, TaskPlugin


class AerospaceSoftwareTask(TaskPlugin):
    name = "aerospace_software"

    def get_targets(self) -> list[SearchTarget]:
        return [
            SearchTarget("NASA Software Catalog", "https://software.nasa.gov/", 0.94),
            SearchTarget("FAA Digital Services", "https://www.faa.gov/about/office_org/headquarters_offices/ang", 0.9),
            SearchTarget("ESA Technology", "https://www.esa.int/Enabling_Support/Space_Engineering_Technology", 0.88),
            SearchTarget("GitHub Aerospace Topics", "https://github.com/topics/aerospace", 0.82),
            SearchTarget("NIST Software Assurance", "https://www.nist.gov/itl/ssd/software-quality-group", 0.86),
        ]

    def keywords(self) -> list[str]:
        return [
            "flight software",
            "telemetry",
            "mission planning",
            "guidance",
            "fault tolerance",
            "verification",
            "avionics",
            "simulation",
            "requirements",
            "aerospace",
        ]

    def objective_boost(self) -> float:
        return 1.15

    def skill_tags(self) -> set[str]:
        return {"software-architecture", "verification", "mission-planning", "source-validation", "evidence-scoring"}
