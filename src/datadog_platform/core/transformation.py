"""
Transformation class for data transformations in pipelines.
"""

from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import ConfigDict, Field

from datadog_platform.core.base import BaseConfig


class Transformation(BaseConfig):
    """
    Represents a data transformation in the orchestration platform.

    Transformations are applied to data as it flows through a pipeline,
    enabling data cleaning, enrichment, aggregation, and other operations.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    transformation_id: str = Field(default_factory=lambda: str(uuid4()))
    function_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    order: int = 0

    def validate_parameters(self) -> bool:
        """
        Validate transformation parameters.

        Returns:
            bool: True if parameters are valid
        """
        if not self.function_name:
            return False

        # Function-specific validation
        required_params = self._get_required_parameters()
        for param in required_params:
            if param not in self.parameters:
                return False

        return True

    def _get_required_parameters(self) -> list[str]:
        """
        Get required parameters for the transformation function.

        Returns:
            list: Required parameter names
        """
        # Define required parameters for built-in transformations
        param_map = {
            "filter_nulls": ["columns"],
            "select_columns": ["columns"],
            "rename_columns": ["mapping"],
            "aggregate": ["group_by", "aggregations"],
            "join": ["right_data", "on", "how"],
            "sort": ["by"],
            "deduplicate": ["subset"],
            "fill_null": ["columns", "value"],
            "cast_types": ["type_mapping"],
            "add_column": ["name", "expression"],
        }
        return param_map.get(self.function_name, [])

    def apply(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Apply the transformation to data (placeholder).

        Args:
            data: Input data to transform
            context: Execution context

        Returns:
            Transformed data
        """
        # This is a placeholder - actual implementation will be in the processing layer
        return data
