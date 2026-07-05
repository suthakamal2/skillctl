# Suggestion Summary

## Prompt: we need to deploy v2 to staging tonight
- **Top bundle**: None
- **Top 3 rules**:
  1. `safe-deploy` (tier 2, triggers: deploy, staging)

## Prompt: the production database query is slow, what indexes should we add
- **Top bundle**: None
- **Top 3 rules**:
  1. `safe-deploy` (tier 2, triggers: production)

## Prompt: set up authentication and authorization for the new API
- **Top bundle**: backend-api
- **Top 3 rules**:
  1. `authentication` (tier 2, triggers: authentication)
  2. `authorization` (tier 2, triggers: authorization)

## Prompt: we have a sev1 outage, walk me through incident response
- **Top bundle**: None
- **Top 3 rules**:
  1. `incident-response` (tier 2, triggers: incident, outage, sev1)

## Prompt: add pagination and rate limiting to this endpoint
- **Top bundle**: None
- **Top 3 rules**:
  1. `api-design` (tier 2, triggers: endpoint)
  2. `pagination` (tier 2, triggers: pagination)

## Prompt: make this React component accessible
- **Top bundle**: None
- **Top 3 rules**:
  1. `component-design` (tier 2, triggers: component, react)

## Prompt: process these events asynchronously off a queue
- **Top bundle**: None
- **Top 3 rules**:
  1. `queue-processing` (tier 2, triggers: queue)

## Prompt: rotate our API keys and audit dependencies for CVEs
- **Top bundle**: None
- **Top 3 rules**:
  1. `dependency-audit` (tier 2, triggers: audit)

## Prompt: write a database migration that adds a nullable column
- **Top bundle**: None
- **Top 3 rules**:
  1. `database-migrations` (tier 2, triggers: migration)

## Prompt: review this pull request before we merge
- **Top bundle**: review-ready
- **Top 3 rules**:
  1. `git-workflow` (tier 2, triggers: merge, pull request)
  2. `code-review` (tier 2, triggers: review)
