# Future Work

## Priority 1 — Statistical Enhancements

### Sequential Testing with Early Stopping
Current limitation: experiment must run to predetermined sample
size before any decision can be made.

Enhancement: implement O'Brien-Fleming alpha spending function
that allows the team to peek at results without inflating
Type I error rate.

```python
# Planned implementation
from scipy.stats import norm

def obrien_fleming_boundary(t, alpha=0.05):
    """
    t = fraction of planned sample collected (0 to 1)
    Returns the z-score boundary at this interim look.
    """
    return norm.ppf(1 - alpha / (2 * t))
```

Business value: allows experiment termination 30-40% earlier
when effect is very large, freeing up traffic for other tests.

### DoWhy Causal Inference Integration
Current limitation: platform shows correlation between variant
assignment and outcome but cannot validate causal identification.

Enhancement: add DoWhy backdoor criterion check that verifies
the causal graph assumptions are satisfied before reporting results.

Business value: prevents false positives from unmeasured confounders.

### Heterogeneous Treatment Effects
Current limitation: reports a single average treatment effect
for the entire user population.

Enhancement: implement causal forests or meta-learners to identify
which user segments (country, device, spend tier) benefit most
from the treatment.

Business value: enables targeted rollout to high-benefit segments
rather than binary ship/no-ship decisions.

---

## Priority 2 — Engineering Enhancements

### PostgreSQL + Docker Production Stack
Replace SQLite with PostgreSQL for concurrent write support.
Containerise with Docker Compose for reproducible deployment.

```yaml
# Planned docker-compose.yml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: experimentos
  app:
    build: .
    depends_on: [db]
    ports: ["8501:8501"]
```

### Real-Time Streaming via Kafka
Replace batch loading with a Kafka producer-consumer pipeline
so experiment results update as events arrive rather than
requiring a manual database reload.

### Multi-Metric Experiment Support
Current limitation: tests one metric at a time (conversion rate).

Enhancement: simultaneous monitoring of primary metric
(conversion rate) plus guardrail metrics (revenue per user,
session length) with automatic alerts if guardrails are violated.

---

## Priority 3 — Product Enhancements

### Slack Integration
Post experiment results automatically to a Slack channel
when significance threshold is reached.

### Experiment Registry
Track all past experiments — hypothesis, duration, result,
decision made — in a searchable database to prevent
re-running experiments that have already been answered.

### Power Analysis Calculator
Interactive tool that takes baseline rate, minimum detectable
effect, and desired power and returns:
- Required sample size
- Expected duration
- CUPED-adjusted duration
- Estimated business impact of detected effect
