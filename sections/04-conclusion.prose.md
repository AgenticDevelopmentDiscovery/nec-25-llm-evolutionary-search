# Conclusion

## What you can do now

After this tutorial, the reader should be able to design a minimal LLM-guided evolutionary search loop, explain the role of the evaluation harness as the selective pressure, and reason about diversity and fitness design as levers on the search. The reader can also recognize a gameable fitness function and ask for held-out or validation checks before treating a candidate as credible.

## Where to go next

The next step is to read the FunSearch paper and compare it with the open OpenEvolve workflow, because they show the same architecture in two different levels of complexity. After that, the useful next topic is a more complete treatment of fitness design and response to reward hacking, since that is the design choice that determines whether the search discovers a solution or a scorer shortcut.

## Open edges

The field is still rapidly changing. There is not yet one best way to structure parent prompts, maintain diversity, or choose a sampling budget. The right design remains contextual: the task, the evaluator, the code environment, and the way the model is allowed to propose edits all shape what it is reasonable to recommend.
