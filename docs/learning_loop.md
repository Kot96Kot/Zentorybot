# Learning Loop for Action Center

The Learning Loop records what happened after an Action Center recommendation so Zentorybot can learn which rules work. It is mock-only and never marks a recommendation as successful without post-action metrics.

## Lifecycle

1. **Action proposed**
   - `action_id`
   - `agent`
   - `sku`
   - `recommendation`
   - `expected_effect`
   - `metric_before`

2. **Action approved**
   - `approved_by`
   - `approved_at`

3. **Action executed**
   - `executed_at`
   - `execution_status`

4. **Review period completed**
   - `metric_after`
   - `effect`
   - `success_score`
   - `conclusion`

## Evaluation statuses

- `SUCCESS` — metric improved enough to strengthen the rule.
- `PARTIAL_SUCCESS` — metric improved, but not enough to strengthen automatically.
- `FAILED` — metric did not improve or execution failed.
- `INCONCLUSIVE` — post-action data is missing.

If `metric_after` is missing, the result is always `INCONCLUSIVE`. The bot does not claim success without metrics.

## Example

Before:

- ДРР: 18%
- bid: 690

Action:

- reduce bid by 15%

After:

- ДРР: 12%
- orders did not drop

Conclusion:

- `action_success=true`
- `status=SUCCESS`
- rule can be strengthened

## API endpoints

- `POST /learning/action-result`
- `GET /learning/actions`
- `GET /learning/sku/{sku}`

## Telegram commands

- `/action_result <action_id>`
- `/learning <sku>`

## Safety

- Mock mode is explicit in schemas and responses.
- No marketplace or payment changes are made.
- Results are recommendations for future ranking only.
- Missing after-metrics produce `INCONCLUSIVE`, not success.
