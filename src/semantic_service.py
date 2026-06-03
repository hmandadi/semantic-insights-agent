"""Semantic Service module.

Provides a thin, object‑oriented wrapper around the ``semantic_manifest.yaml``
file.  The service loads the manifest using **PyYAML** and offers convenient
methods for retrieving metrics, dimensions, and relationships.

All public methods raise ``KeyError`` when a requested name does not exist,
making error handling explicit for callers.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class SemanticService:
    """Service for accessing the semantic manifest.

    The manifest is loaded once at instantiation.  It is expected to follow the
    structure produced by the earlier task (tables, metrics, dimensions, etc.).
    """

    def __init__(self, manifest_path: str | None = None) -> None:
        """Create a new ``SemanticService``.

        Args:
            manifest_path: Optional absolute or relative path to the YAML file.
                If omitted, ``config/semantic_manifest.yaml`` relative to the
                project root is used.
        """
        default_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "config", "semantic_manifest.yaml")
        )
        self.manifest_path = os.path.abspath(manifest_path) if manifest_path else default_path
        self._manifest: Dict[str, Any] = {}
        self.load_manifest()

    def load_manifest(self) -> None:
        """Load the YAML manifest from ``self.manifest_path``.

        Raises:
            FileNotFoundError: If the manifest file does not exist.
            yaml.YAMLError: If the file cannot be parsed.
        """
        logger.info("Loading semantic manifest from %s", self.manifest_path)
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Semantic manifest not found: {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            try:
                self._manifest = yaml.safe_load(f) or {}
            except yaml.YAMLError as exc:
                logger.exception("Failed to parse semantic manifest: %s", exc)
                raise

    # ---------------------------------------------------------------------
    # Helper accessors
    # ---------------------------------------------------------------------
    def _get_section(self, section: str) -> Dict[str, Any]:
        """Return a section of the manifest (e.g., ``metrics``) or an empty dict.
        """
        return self._manifest.get(section, {}) or {}

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def get_metric(self, metric_name: str) -> Dict[str, Any]:
        """Retrieve a metric definition by name.

        Raises:
            KeyError: If the metric is not defined.
        """
        metrics = self._get_section("metrics")
        if metric_name not in metrics:
            raise KeyError(f"Metric '{metric_name}' not found in manifest")
        return metrics[metric_name]

    def get_dimension(self, dimension_name: str) -> Dict[str, Any]:
        """Retrieve a dimension definition by name.

        Raises:
            KeyError: If the dimension is not defined.
        """
        dimensions = self._get_section("dimensions")
        if dimension_name not in dimensions:
            raise KeyError(f"Dimension '{dimension_name}' not found in manifest")
        return dimensions[dimension_name]

    def get_relationships(self) -> Dict[str, Any]:
        """Return the ``relationships`` section from the manifest.

        The relationships are defined under each table; this method aggregates
        them into a dictionary keyed by table name.
        """
        tables = self._get_section("tables")
        rels: Dict[str, Any] = {}
        for table_name, table_def in tables.items():
            if isinstance(table_def, dict) and "relationships" in table_def:
                rels[table_name] = table_def["relationships"]
        return rels

    def list_metrics(self) -> List[str]:
        """Return a list of all metric names defined in the manifest."""
        return list(self._get_section("metrics").keys())

    def list_dimensions(self) -> List[str]:
        """Return a list of all dimension names defined in the manifest."""
        return list(self._get_section("dimensions").keys())

    def get_manifest(self) -> Dict[str, Any]:
        """Return the full manifest dictionary."""
        return self._manifest
