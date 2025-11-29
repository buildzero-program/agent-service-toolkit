"""
Template Variable Processor for System Prompts.

Processes @variable placeholders in system prompts, replacing them with actual values.
Supports dot notation for variations: @current_datetime.weekday, @current_datetime.time

AST-native variables (processed here):
- @current_datetime (and all variations)
- @model_name
- @thread_id

Context variables (preserved for Core processing):
- @contact_name, @contact_phone, @contact_email
- @channel_name, @channel_type, @agent_phone
- @organization_name
"""

from datetime import datetime
import re
from typing import Callable


# ═══════════════════════════════════════════════════════════════════════════════
# REGEX PATTERN
# ═══════════════════════════════════════════════════════════════════════════════

# Pattern: @variable or @variable.variation or @variable.sub.variation
# Examples: @model_name, @current_datetime.weekday, @current_datetime.date.iso
VARIABLE_PATTERN = re.compile(r"@(\w+(?:\.\w+)*)")


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS - Portuguese translations
# ═══════════════════════════════════════════════════════════════════════════════

WEEKDAYS_PT = [
    "segunda-feira",  # Monday = 0 in Python
    "terça-feira",    # Tuesday = 1
    "quarta-feira",   # Wednesday = 2
    "quinta-feira",   # Thursday = 3
    "sexta-feira",    # Friday = 4
    "sábado",         # Saturday = 5
    "domingo",        # Sunday = 6
]

MONTHS_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


# ═══════════════════════════════════════════════════════════════════════════════
# DATETIME RESOLVER
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_datetime(variation: str, now: datetime) -> str:
    """
    Resolve @current_datetime variations.

    Args:
        variation: The variation suffix (empty string for default, or "iso", "date", etc.)
        now: The datetime to format

    Returns:
        Formatted datetime string in PT-BR
    """
    pad = lambda n: str(n).zfill(2)

    day = pad(now.day)
    month = pad(now.month)
    year = str(now.year)
    hours = pad(now.hour)
    minutes = pad(now.minute)
    seconds = pad(now.second)

    weekday = WEEKDAYS_PT[now.weekday()]
    month_name = MONTHS_PT[now.month - 1]

    match variation:
        case "" | None:
            return f"{weekday}, {now.day} de {month_name} de {year} às {hours}:{minutes}"
        case "iso":
            return f"{year}-{month}-{day}T{hours}:{minutes}:{seconds}"
        case "date":
            return f"{day}/{month}/{year}"
        case "date.iso":
            return f"{year}-{month}-{day}"
        case "date.us":
            return f"{month}/{day}/{year}"
        case "time":
            return f"{hours}:{minutes}"
        case "time.full":
            return f"{hours}:{minutes}:{seconds}"
        case "weekday":
            return weekday
        case "day":
            return str(now.day)
        case "month":
            return month_name
        case "month.num":
            return str(now.month)
        case "year":
            return year
        case _:
            # Unknown variation - return default format
            return f"{weekday}, {now.day} de {month_name} de {year} às {hours}:{minutes}"


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

def process_template_variables(
    template: str,
    model_name: str,
    thread_id: str,
) -> str:
    """
    Process @variable placeholders in system prompt.

    Only processes AST-native variables:
    - @current_datetime (and variations like .weekday, .time, etc.)
    - @model_name
    - @thread_id

    Context variables (@contact_*, @channel_*, etc.) are preserved for
    Core processing.

    Args:
        template: The system prompt template with @variables
        model_name: The LLM model name (e.g., "grok-4-1-fast")
        thread_id: The conversation thread ID

    Returns:
        Processed template with AST variables replaced
    """
    now = datetime.now()

    def replace_variable(match: re.Match) -> str:
        full_path = match.group(1)
        parts = full_path.split(".")
        base_name = parts[0]
        variation = ".".join(parts[1:]) if len(parts) > 1 else ""

        match base_name:
            case "current_datetime":
                return resolve_datetime(variation, now)
            case "model_name":
                return model_name
            case "thread_id":
                return thread_id
            case _:
                # Keep original for unknown variables (will be processed by Core)
                return match.group(0)

    return VARIABLE_PATTERN.sub(replace_variable, template)
