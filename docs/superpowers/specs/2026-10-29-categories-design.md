# Categories: Earn, Career, Home

Date: 2026-10-29. Status: approved by Stephen in conversation. Replaces the `money` / `time` / `life` categories from the 2026-10-23 design.

## Why

Stephen is between roles, so "saves hours in professional work" is not a goal he has. What he has is a job search and a wish for income, alongside the household.

## Categories

| id | Label | Meaning |
|---|---|---|
| `earn` | Earn | Makes money now |
| `career` | Career | Gets him the next role: job search, interview prep, portfolio projects, skills worth a resume line |
| `home` | Home | Home, family, and planning |

## Changes

- `build.py` CATEGORIES, tests, and the fixture generator use the new ids.
- `rubric.md` has a Career column in the Fit and Upside tables and a profile line saying he is between roles. Ideas that only save time in someone else's job go to `career` when they make a credible portfolio project, to `earn` when sellable as a service, and otherwise score low on Fit.
- `ROUTINE.md` names the new categories; the routine re-tags repeat ideas on its next run.
- Existing data was migrated once by id: money to earn, time to career, life to home. The 28 former `time` ideas are therefore `career` until the next run reconsiders them.
- The board shows labels Earn, Career, Home with hover descriptions and a legend line.
