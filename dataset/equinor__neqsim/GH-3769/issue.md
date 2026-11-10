# SystemUNIFAC` throws `ArrayIndexOutOfBoundsException`: the group array and the group list are never synchronised

- Issue: https://github.com/equinor/neqsim/issues/3769
- Opened by PatrickMockridge on 2026-09-17, closed on 2026-09-17
- Labels: bug
- Fix commit: bc240a88a3a56226a303ae8f4c2ae02f288efe94

## Report

**Summary.** `ComponentGEUnifac` keeps each component's UNIFAC groups twice — in an
`ArrayList<UNIFACgroup> unifacGroups` and in a `UNIFACgroup[] unifacGroupsArray`. The
constructor fills only the list, leaving the array at its initial length zero, but
`getNumberOfUNIFACgroups()` reads the *list* while `getUnifacGroup(int)` reads the *array*.
Every loop of the form `for (i = 0; i < getNumberOfUNIFACgroups(); i++) getUnifacGroup(i)`
therefore indexes an empty array and throws. The first such loop is in
`PhaseGEUnifac.setMixingRule` → `checkGroups()`, so a `SystemUNIFAC` cannot be configured at
all. `checkGroups()` cannot repair it either, because its own last step rebuilds the list
*from* the array.

**Environment.** NeqSim 3.20.0, `neqsim-3.20.0.jar` as published.

## Reproduction

```java
import neqsim.thermo.system.SystemUNIFAC;

public class UnifacRepro {
  public static void main(String[] args) {
    SystemUNIFAC system = new SystemUNIFAC(298.15, 1.0);
    system.addComponent("methanol", 0.5);
    system.addComponent("water", 0.5);
    system.createDatabase(true);
    system.setMixingRule("classic");
    System.out.println("setMixingRule returned");
  }
}
```

Output:

```
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 0 out of bounds for length 0
	at neqsim.thermo.component.ComponentGEUnifac.getUnifacGroup(ComponentGEUnifac.java:312)
	at neqsim.thermo.phase.PhaseGEUnifac.checkGroups(PhaseGEUnifac.java:142)
	at neqsim.thermo.phase.PhaseGEUnifac.setMixingRule(PhaseGEUnifac.java:80)
	at neqsim.thermo.system.SystemThermo.setMixingRule(SystemThermo.java:5337)
	at neqsim.thermo.system.SystemInterface.setMixingRule(SystemInterface.java:2532)
	at UnifacRepro.main(UnifacRepro.java:9)
```

`init(0)` throws identically if the mixing rule is set first, by the other route:
`PhaseGEUnifac.init` → `PhaseGE.init` → `getExcessGibbsEnergy` → `ComponentGEUnifac.getGamma`
→ `getR` → `getUnifacGroup(0)`.

## Mechanism

Two fields, one populated:

```java
ArrayList<UNIFACgroup> unifacGroups = new ArrayList<UNIFACgroup>();   // ComponentGEUnifac.java:29
UNIFACgroup[] unifacGroupsArray = new UNIFACgroup[0];                 // ComponentGEUnifac.java:30
```

The constructor adds to the **list** only — `unifacGroups.add(new UNIFACgroup(p, temp))` at
`ComponentGEUnifac.java:75`, inside the loop that reads the subgroup columns. Nothing writes
`unifacGroupsArray` except `setUnifacGroups` (`:320-323`) and `addUNIFACgroup`.

Two accessors disagree about which field is authoritative:

```java
public UNIFACgroup getUnifacGroup(int i) { return unifacGroupsArray[i]; }   // :311-312
public int getNumberOfUNIFACgroups()     { return unifacGroups.size(); }    // :330-332
```

So the length is taken from the list and the index applied to the array. Every consumer
iterates that pair, for example `getR` (`:135-140`) and `checkGroups`
(`PhaseGEUnifac.java:137-143`), and each throws on the first component that has any group.

**`checkGroups()` makes the desynchronisation permanent rather than fixing it.** Its last loop
is:

```java
UNIFACgroup[] array = ((ComponentGEUnifac) getComponent(i)).getUnifacGroups();
java.util.Arrays.sort(array);
ArrayList<UNIFACgroup> phaseList = new ArrayList<UNIFACgroup>(0);
phaseList.addAll(Arrays.asList(array));
((ComponentGEUnifac) getComponent(i)).setUnifacGroups(phaseList);   // PhaseGEUnifac.java:158-163
```

The list is rebuilt *from* the array. Called on an empty array it sets an empty list, so the
one method that could have reconciled the two fields destroys the surviving copy instead. The
order is therefore forced: the array must be synchronised from the list **before**
`checkGroups()` runs, and again if the list is rebuilt.

A caller can work around it — `for each component: c.setUnifacGroups(c.getUnifacGroups2())`
before `setMixingRule` and again after — which is how it was found here. It is not discoverable
from the API, and it must be repeated before every subsequent `init(0)`.

## Impact

`SystemUNIFAC` and `SystemUNIFACpsrk` are unusable as shipped: the exception fires during
configuration, before any calculation. Classic UNIFAC is one of the headline activity models,
so this is not a corner — it is the documented entry point for it.

## Why the test suite misses it

`src/test/java/neqsim/thermo/phase/PhaseGEUnifacTest.java` contains one test:

```java
@Test
void testAddcomponent() {
  Assertions.assertEquals(0, p.getNumberOfComponents());
  p.addComponent("ethane", 0, 0, 0);
  Assertions.assertEquals(1, p.getNumberOfComponents());
  ...
}
```

It asserts a component count and never calls `setMixingRule`, `init`, `getR`, `getQ`, or
anything else that reads a group. Whatever coverage `SystemUNIFAC` has elsewhere does not reach
this path either, since the exception would fail it.

## Proposed fix

**Synchronise before reading, inside `checkGroups()`.** One loop at the top of the method:

```java
public void checkGroups() {
  // The constructor fills the list; every reader below indexes the array.
  for (int i = 0; i < numberOfComponents; i++) {
    ComponentGEUnifac c = (ComponentGEUnifac) getComponent(i);
    c.setUnifacGroups(c.getUnifacGroups2());
  }
  ... // the existing body
}
```

This is the smallest change that keeps `checkGroups()` callable more than once, which it must
be: it rebuilds the list, so the array has to be re-derived from it on each call.

**Alternatively**, have the constructor end with `setUnifacGroups(unifacGroups)` so the two
fields agree from construction. That fixes the first throw but not a later `checkGroups()` call
after the list has been rebuilt, so the first option is preferred.

A third possibility worth considering is removing one of the two fields entirely —
`getUnifacGroups2()` and `setUnifacGroups` exist only to paper over the split — but that is a
wider change than a bug fix.

## Comment by EvenSol on 2026-09-17

Thanks for reporting - will look into it.
