# Problem Statement

## Background

Most A/B testing fails quietly. Not because the statistics are wrong
but because nobody knows what they are actually measuring, the test
runs too long so someone calls it early, the result gets written up
inconsistently, and three months later nobody can explain why that
feature shipped. This happens at companies with smart people and good
intentions. It is a tooling problem, not a talent problem.

## Core Problems

### Problem 1 — Frequentist p-values are misinterpreted

The standard A/B test outputs a p-value. Academic research shows
that 70%+ of practitioners misinterpret what p < 0.05 actually means.
A p-value does not tell you the probability that the treatment is better.
It tells you the probability of seeing this data if there were no effect —
a completely different, non-actionable statement.

Product managers make ship/kill decisions based on a number that
does not answer the question they are actually asking.

### Problem 2 — Experiments run too long

High variance in user metrics means experiments need large sample
sizes to detect real effects. At a typical e-commerce conversion rate
of 3-5%, detecting a 10% relative improvement requires:
n = 2 × ((z_α + z_β) / MDE)² × variance
n ≈ 8,400 users per variant at 5% baseline, 10% MDE

At 500 new users per day, that is 17 days per variant — 34 days total.
Most companies run 10-50 experiments simultaneously.
This creates a bottleneck that slows the entire product roadmap.

### Problem 3 — Metric definition inconsistency

The engineering team defines revenue as gross transaction value.
The product team defines it as net of refunds.
The finance team defines it as recognised revenue after 30-day hold.

When these three teams analyse the same experiment, they get
three different answers. Alignment meetings replace product work.
Stripe publicly described this as costing their teams weeks per sprint.

### Problem 4 — No governed change management for metrics

When a data analyst changes the SQL definition of "active user"
from "any event in 30 days" to "purchase event in 30 days",
every dashboard, experiment, and business review using that metric
silently breaks. No notification. No review. No audit trail.

### Problem 5 — Decision documentation is manual and inconsistent

After an experiment concludes, someone writes a memo explaining
the results to stakeholders. This takes 1-2 hours, gets written
inconsistently, and often omits the statistical context that would
help the team make a better decision next time.

## Quantified Business Impact

| Company | Public statement about this problem |
|---|---|
| Airbnb | Built Chronon and Superset specifically for metric governance |
| Netflix | Published "Innovating Faster on Personalisation with Interleaving" citing CUPED |
| LinkedIn | Published "Trustworthy Online Controlled Experiments" — entire book on this |
| DoorDash | Engineering blog: underpowered experiments cited as #1 data team problem |
| Stripe | Engineering blog: metric inconsistency costs weeks per sprint in alignment |

Estimated annual cost of poor experimentation infrastructure
at a mid-size product company (500 engineers):
- Delayed decisions: $2-5M in slower product velocity
- Wrong decisions from misinterpreted tests: $1-3M in wasted build
- Alignment overhead: $500K-1M in engineering hours

## What ExperimentOS Solves

ExperimentOS replaces ad-hoc experimentation with a governed,
statistically rigorous platform that:

1. Produces Bayesian posterior distributions that answer
   "what is the probability B is better?" directly
2. Implements CUPED to reduce experiment duration by 30-50%
3. Enforces a single canonical metric definition via dbt
4. Blocks unapproved metric changes via GitHub Actions gate
5. Auto-generates decision memos so no context is lost
