"""Tests for template variable processor - @current_datetime, @model_name, @thread_id."""

from datetime import datetime
from unittest.mock import patch

import pytest


class TestResolveDateTime:
    """Test resolve_datetime() function with all variations."""

    @pytest.fixture
    def fixed_datetime(self):
        """Fixed datetime for deterministic tests: Friday, November 28, 2025 at 14:30:45"""
        return datetime(2025, 11, 28, 14, 30, 45)

    def test_default_format(self, fixed_datetime):
        """Test @current_datetime without variation - natural PT-BR format."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("", fixed_datetime)
        assert result == "sexta-feira, 28 de novembro de 2025 às 14:30"

    def test_iso_format(self, fixed_datetime):
        """Test @current_datetime.iso - ISO 8601 format."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("iso", fixed_datetime)
        assert result == "2025-11-28T14:30:45"

    def test_date_br_format(self, fixed_datetime):
        """Test @current_datetime.date - Brazilian date format."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("date", fixed_datetime)
        assert result == "28/11/2025"

    def test_date_iso_format(self, fixed_datetime):
        """Test @current_datetime.date.iso - ISO date format."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("date.iso", fixed_datetime)
        assert result == "2025-11-28"

    def test_date_us_format(self, fixed_datetime):
        """Test @current_datetime.date.us - US date format."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("date.us", fixed_datetime)
        assert result == "11/28/2025"

    def test_time_format(self, fixed_datetime):
        """Test @current_datetime.time - time without seconds."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("time", fixed_datetime)
        assert result == "14:30"

    def test_time_full_format(self, fixed_datetime):
        """Test @current_datetime.time.full - time with seconds."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("time.full", fixed_datetime)
        assert result == "14:30:45"

    def test_weekday(self, fixed_datetime):
        """Test @current_datetime.weekday - day of week in PT-BR."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("weekday", fixed_datetime)
        assert result == "sexta-feira"

    def test_day(self, fixed_datetime):
        """Test @current_datetime.day - day of month."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("day", fixed_datetime)
        assert result == "28"

    def test_month_name(self, fixed_datetime):
        """Test @current_datetime.month - month name in PT-BR."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("month", fixed_datetime)
        assert result == "novembro"

    def test_month_num(self, fixed_datetime):
        """Test @current_datetime.month.num - month number."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("month.num", fixed_datetime)
        assert result == "11"

    def test_year(self, fixed_datetime):
        """Test @current_datetime.year - full year."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("year", fixed_datetime)
        assert result == "2025"

    def test_unknown_variation_returns_default(self, fixed_datetime):
        """Test unknown variation falls back to default format."""
        from agents.template_processor import resolve_datetime

        result = resolve_datetime("unknown_variation", fixed_datetime)
        assert result == "sexta-feira, 28 de novembro de 2025 às 14:30"

    def test_all_weekdays(self):
        """Test all days of the week are correctly translated to PT-BR."""
        from agents.template_processor import resolve_datetime

        # Sunday = 0 in our list
        test_cases = [
            (datetime(2025, 11, 23, 12, 0), "domingo"),      # Sunday
            (datetime(2025, 11, 24, 12, 0), "segunda-feira"), # Monday
            (datetime(2025, 11, 25, 12, 0), "terça-feira"),   # Tuesday
            (datetime(2025, 11, 26, 12, 0), "quarta-feira"),  # Wednesday
            (datetime(2025, 11, 27, 12, 0), "quinta-feira"),  # Thursday
            (datetime(2025, 11, 28, 12, 0), "sexta-feira"),   # Friday
            (datetime(2025, 11, 29, 12, 0), "sábado"),        # Saturday
        ]

        for dt, expected_weekday in test_cases:
            result = resolve_datetime("weekday", dt)
            assert result == expected_weekday, f"Failed for {dt}: expected {expected_weekday}, got {result}"

    def test_all_months(self):
        """Test all months are correctly translated to PT-BR."""
        from agents.template_processor import resolve_datetime

        months = [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]

        for month_num, expected_month in enumerate(months, start=1):
            dt = datetime(2025, month_num, 15, 12, 0)
            result = resolve_datetime("month", dt)
            assert result == expected_month, f"Failed for month {month_num}: expected {expected_month}, got {result}"


class TestProcessTemplateVariables:
    """Test process_template_variables() function."""

    @pytest.fixture
    def fixed_datetime(self):
        """Fixed datetime for deterministic tests."""
        return datetime(2025, 11, 28, 14, 30, 45)

    def test_no_variables(self):
        """Test template with no variables."""
        from agents.template_processor import process_template_variables

        template = "Hello, this is a simple prompt."
        result = process_template_variables(template, "gpt-4", "thread-123")
        assert result == "Hello, this is a simple prompt."

    def test_model_name_variable(self):
        """Test @model_name replacement."""
        from agents.template_processor import process_template_variables

        template = "You are using @model_name"
        result = process_template_variables(template, "grok-4-1-fast", "thread-123")
        assert result == "You are using grok-4-1-fast"

    def test_thread_id_variable(self):
        """Test @thread_id replacement."""
        from agents.template_processor import process_template_variables

        template = "Thread ID: @thread_id"
        result = process_template_variables(template, "gpt-4", "abc-123-xyz")
        assert result == "Thread ID: abc-123-xyz"

    def test_current_datetime_default(self, fixed_datetime):
        """Test @current_datetime replacement with mocked time."""
        from agents.template_processor import process_template_variables

        with patch("agents.template_processor.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime

            template = "Today is @current_datetime"
            result = process_template_variables(template, "gpt-4", "thread-123")
            assert result == "Today is sexta-feira, 28 de novembro de 2025 às 14:30"

    def test_current_datetime_variations(self, fixed_datetime):
        """Test @current_datetime with various dot notations."""
        from agents.template_processor import process_template_variables

        with patch("agents.template_processor.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime

            template = "Date: @current_datetime.date Time: @current_datetime.time Weekday: @current_datetime.weekday"
            result = process_template_variables(template, "gpt-4", "thread-123")
            assert result == "Date: 28/11/2025 Time: 14:30 Weekday: sexta-feira"

    def test_multiple_variables(self, fixed_datetime):
        """Test template with multiple different variables."""
        from agents.template_processor import process_template_variables

        with patch("agents.template_processor.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime

            template = "Model: @model_name | Thread: @thread_id | Time: @current_datetime.time"
            result = process_template_variables(template, "claude-3", "my-thread")
            assert result == "Model: claude-3 | Thread: my-thread | Time: 14:30"

    def test_unknown_variable_preserved(self):
        """Test that unknown @variables are preserved (for Core processing)."""
        from agents.template_processor import process_template_variables

        template = "Hello @contact_name.first! Using @model_name"
        result = process_template_variables(template, "gpt-4", "thread-123")
        # @contact_name.first should be preserved, @model_name should be replaced
        assert result == "Hello @contact_name.first! Using gpt-4"

    def test_variable_at_start(self):
        """Test variable at the start of template."""
        from agents.template_processor import process_template_variables

        template = "@model_name is the model"
        result = process_template_variables(template, "gpt-4", "thread-123")
        assert result == "gpt-4 is the model"

    def test_variable_at_end(self):
        """Test variable at the end of template."""
        from agents.template_processor import process_template_variables

        template = "Using model @model_name"
        result = process_template_variables(template, "gpt-4", "thread-123")
        assert result == "Using model gpt-4"

    def test_adjacent_variables(self):
        """Test adjacent variables without space."""
        from agents.template_processor import process_template_variables

        template = "@model_name/@thread_id"
        result = process_template_variables(template, "gpt-4", "thread-123")
        assert result == "gpt-4/thread-123"

    def test_email_not_treated_as_variable(self):
        """Test that email addresses are not treated as variables."""
        from agents.template_processor import process_template_variables

        # This is tricky - @domain.com could match our pattern
        # But since "domain" is not a known variable, it should be preserved
        template = "Contact: user@example.com"
        result = process_template_variables(template, "gpt-4", "thread-123")
        assert result == "Contact: user@example.com"

    def test_complex_system_prompt(self, fixed_datetime):
        """Test a realistic system prompt with multiple variables."""
        from agents.template_processor import process_template_variables

        with patch("agents.template_processor.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime

            template = """Você é um assistente virtual.

Hoje é @current_datetime.weekday, @current_datetime.day de @current_datetime.month de @current_datetime.year, às @current_datetime.time.

Você está usando o modelo @model_name.
ID da conversa: @thread_id

Informações do contato: @contact_name.first pelo @channel_type."""

            result = process_template_variables(template, "grok-4", "conv-abc-123")

            expected = """Você é um assistente virtual.

Hoje é sexta-feira, 28 de novembro de 2025, às 14:30.

Você está usando o modelo grok-4.
ID da conversa: conv-abc-123

Informações do contato: @contact_name.first pelo @channel_type."""

            assert result == expected


class TestVariablePattern:
    """Test the regex pattern for variable detection."""

    def test_simple_variable(self):
        """Test simple @variable pattern."""
        from agents.template_processor import VARIABLE_PATTERN

        text = "@model_name"
        matches = VARIABLE_PATTERN.findall(text)
        assert matches == ["model_name"]

    def test_variable_with_dot(self):
        """Test @variable.variation pattern."""
        from agents.template_processor import VARIABLE_PATTERN

        text = "@current_datetime.weekday"
        matches = VARIABLE_PATTERN.findall(text)
        assert matches == ["current_datetime.weekday"]

    def test_variable_with_multiple_dots(self):
        """Test @variable.sub.variation pattern."""
        from agents.template_processor import VARIABLE_PATTERN

        text = "@current_datetime.date.iso"
        matches = VARIABLE_PATTERN.findall(text)
        assert matches == ["current_datetime.date.iso"]

    def test_multiple_variables(self):
        """Test multiple variables in text."""
        from agents.template_processor import VARIABLE_PATTERN

        text = "@model_name and @thread_id and @current_datetime.time"
        matches = VARIABLE_PATTERN.findall(text)
        assert matches == ["model_name", "thread_id", "current_datetime.time"]

    def test_variable_boundaries(self):
        """Test that variables are properly bounded."""
        from agents.template_processor import VARIABLE_PATTERN

        text = "start@model_name end"  # @ not at word boundary
        matches = VARIABLE_PATTERN.findall(text)
        assert matches == ["model_name"]  # Still matches after @
