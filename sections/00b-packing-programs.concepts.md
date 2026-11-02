# 00b-packing-programs — teaching spine

## Claims

- Greedy Local Center Search repeatedly proposes a center move, reallocates valid radii, and accepts only a strict score increase.
- Move scale controls the standard deviation of coordinate changes before clipping; it is neither a fixed nor a maximum displacement.
- Move acceptance operates inside one program; source mutation and program selection operate in the outer evolutionary loop.
- One trial is one execution of fixed source from one specified start, seed and work request.
- Three common trial conditions define a bank-comparable program evaluation; defaults map trials 1/2/3 to seeds 3/4/5.
- A trial can contain many numerical search steps and progress reports; neither is a new model call.

## Decisions

- User requested algorithm and trial explanations before the terminology appears in mutation or fitness.
- Add two prerequisite frames after the geometric problem and before Chapter 10, preserving its existing 2/3/2/1/2 frame allocation.
- Use full method names and the actual disclosed numerical mechanism.
- Define requested steps, hard time cap, seed and packing bank before later slides depend on them.
- Main plan remains within 20–25 minutes; architecture appendix is optional discussion beyond the timed main talk.

## Open questions

- Actual aloud timing remains a presenter action.

## Not doing

- No numerical, source-generation, seeding, selection or API-budget changes.
- No claim that equal seeds force identical moves in different programs or that every program performs exactly 80 steps.
