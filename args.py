import argparse

from src.core.project_state import ProjectState

# Parser instance
_parser = argparse.ArgumentParser(description='Fastapi application')

# Add arguments
_parser.add_argument(
    '--state',
    type=ProjectState,
    choices=list(ProjectState),
    help='Specify the state (choose from {})'.format('/'.join([e.value for e in ProjectState])),
    default=ProjectState.DEBUG
)

# Parse
cmd_args = _parser.parse_args()
