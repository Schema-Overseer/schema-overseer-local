# Principles

**Key idea**: fail-fast – push the detection of issues to the earliest stages of development

1. Strict contracting
	- technical: it is a foundation for reliable and scalable system, it is better to think about it early
	- communication: it pushes developers to establish communication protocols and rules and follow them
	- mindset: motivates developers to think ahead and don't change schemas too often, improving the architectural thinking and saving resources on refactoring

2. Heavy use of type hinting
	- type hinting is described in builder
	- your IDE will suggest you right types (don't forget to use mypy!)

3. Development stage validation
	- motivates (something more stronger?) use of strict contracts on the development stage

4. Build stage validation
	- when building a project you will catch any unsychronized contracts

5. Runtime validation
	- when running a project you will catch any unsychronized contracts

## Consequences / Long-term Benefits

In addition to short-term benefits such as catching issues earlier, our approach brings long-term benefits.

1. Better extensibility

2. Improved observability

3. Cultural shift
- communication
- mindset