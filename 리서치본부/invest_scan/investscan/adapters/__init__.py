"""
investscan/adapters — Bridge adapters for standalone external systems.

Each adapter reads the OUTPUT of an independent system without modifying it.
Both EnvironmentScan and GlobalNews remain fully standalone programs.

Adapters:
  envscan_adapter   — reads EnvironmentScan output/WF*.json files
  gnews_adapter     — reads GlobalNews data/output/{date}/signals.parquet
"""
