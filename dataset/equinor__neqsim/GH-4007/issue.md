# Vega forced-liquid phase uses vapor density root and publishes nonphysical Cp

- Issue: https://github.com/equinor/neqsim/issues/4007
- Opened by EvenSol on 2026-09-25, closed on 2026-09-26
- Labels: bug
- Fix commit: 7e5cc35b84b8cf0f832705734eb5192b7ac4eeb0

## Report

## Problem

At exact master `83d27a570c430724d97e2ea70de67a810f10d74b`, the helium Vega System/Phase path does not honor a forced liquid phase when solving density. `NeqSimVega.getMolarDensity()` always calls `Vega.DensityVega` with `iFlag = 0`, which the production Javadoc defines as the gas-phase solver; `iFlag = 2` is the liquid-root search.

This was found while adding sourced per-model numerical specifications under #3792.

## Minimal reproducer

```java
SystemVegaEos system = new SystemVegaEos(4.0, 2.0);
system.setNumberOfPhases(1);
system.setMaxNumberOfPhases(1);
system.setForcePhaseTypes(true);
system.setPhaseType(0, PhaseType.LIQUID);
system.init(3);

PhaseVegaEos phase = (PhaseVegaEos) system.getPhase(0);
NeqSimVega vega = new NeqSimVega(phase);
System.out.println(vega.getMolarDensity());
System.out.println(phase.getZ());
System.out.println(phase.getCp("J/molK"));
```

Observed NeqSim results:

- 4 K, 2 bar(a): 3.189294954 mol/L, Z = 1.000001191, Cp = -174.065906 J/(mol K)
- 3 K, 1 bar(a): 2.151296613 mol/L, Z = 1.000001191, Cp = 780.950806 J/(mol K)

Independent CoolProp 7.2.0 `PropsSI` anchors using the versioned [Helium.json](https://github.com/CoolProp/CoolProp/blob/v7.2.0/dev/fluids/Helium.json) Ortiz-Vega EOS:

- 4 K, 2 bar(a), liquid: 33.446484273 mol/L, Z = 0.1797982634, Cp = 15.15132388 J/(mol K)
- 3 K, 1 bar(a), liquid: 35.746312243 mol/L, Z = 0.1121536631, Cp = 10.04780424 J/(mol K)

## Expected contract

The forced-liquid path should select the intended liquid root or fail explicitly. It must not silently publish a gas/metastable root and nonphysical caloric properties as the requested liquid state.

## Scope and coordination

The #3792 qualification batch will cover only four verified gas/supercritical states and will keep liquid Vega behavior as explicit debt. A fix should preserve the existing gas path, propagate density-solver errors instead of accepting an ideal fallback, and add direct gas/liquid root-selection and state-publication tests. Flashes, saturation and transport remain outside this reproducer.

## Comment by EvenSol on 2026-09-25

The fix is in draft PR #4012. It selects the Vega liquid root, corrects the density and Cp derivatives, rejects solver fallbacks and gas-like liquid roots, and adds liquid benchmarks plus phase-switch and repeat-initialization regressions. The affected local tests and formatting gates pass. Java 8/21 model-specification and javadoc hosted jobs have passed; the remaining hosted checks are still running. This issue stays open until the PR is merged.
