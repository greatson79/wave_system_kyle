# Orchestrator Logic

IF intent == sermon:
  run sermon pipeline
ELIF intent == discipleship:
  run discipleship pipeline
ELIF intent == operations:
  run operations pipeline
ELSE:
  fallback

Aggregation:
- merge outputs
- validate theology
