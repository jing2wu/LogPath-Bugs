# NullPointerException creating SubstationGraph with line

- Issue: https://github.com/powsybl/powsybl-diagram/issues/534
- Opened by tadam50 on 2023-07-17, closed on 2023-07-19
- Labels: bug, SLD
- Fix commit: b2277094031df3fed6f25c2d3fd029654f909ccd

## Report

### Describe the current behavior

With:
- `ssb1`: a `SubstationRawBuilder`
- `ssb2`: a `SubstationRawBuilder`

If we use the `SubstationRawBuilder::createLine` method from `ssb1` to create a line between two substations `ssb1` & `ssb2`.
A `LineEdge` will be added into `ssb1` using RawGraphBuilder::buildSubstationGraph(`ssb1`);

When we want to build a substation graph from horizontal or vertical layout an exception is raised.
Indeed we are looking for a voltagelevel graph which is not in the substation to build.
This case is not managed. 

### Describe the expected behavior

No null exception must be raised.
A assertion can be raised to the user to warn him of misuse ?

### Describe the steps

In TestCase11SubstationGraph replace :
`Map<VoltageLevelRawBuilder, FeederNode> line1 = ssb2.createLine("line1", vlb1, vlsubst2, 7, 1, TOP, TOP);`
by
`Map<VoltageLevelRawBuilder, FeederNode> line1 = ssb1.createLine("line1", vlb1, vlsubst2, 7, 1, TOP, TOP);`

The following exception is raised in tests  testH():
java.lang.NullPointerException: Cannot invoke "com.powsybl.sld.model.graphs.VoltageLevelGraph.getX()" because "vlGraph2" is null

and testV():
java.lang.NullPointerException: Cannot invoke "com.powsybl.sld.model.graphs.VoltageLevelInfos.getId()" because the return value of "com.powsybl.sld.model.graphs.SubstationGraph.getVoltageLevelInfos(com.powsybl.sld.model.nodes.Node)" is null

### Environment

_No response_

### Relevant Log Output

testV():
com.powsybl.sld.layout.VerticalSubstationLayout.addMiddlePoints(VerticalSubstationLayout.java:174)
	at com.powsybl.sld.layout.VerticalSubstationLayout.calculatePolylineSnakeLine(VerticalSubstationLayout.java:144)
	at com.powsybl.sld.layout.AbstractLayout.manageSnakeLines(AbstractLayout.java:55)
	at com.powsybl.sld.layout.VerticalSubstationLayout.manageSnakeLines(VerticalSubstationLayout.java:70)
	at com.powsybl.sld.layout.AbstractSubstationLayout.run(AbstractSubstationLayout.java:37)
	at com.powsybl.sld.raw.TestCase11SubstationGraph.testV(TestCase11SubstationGraph.java:301)

testH():
com.powsybl.sld.layout.AbstractLayout.addMiddlePoints(AbstractLayout.java:175)
	at com.powsybl.sld.layout.AbstractLayout.calculatePolylineSnakeLineForHorizontalLayout(AbstractLayout.java:151)
	at com.powsybl.sld.layout.HorizontalSubstationLayout.calculatePolylineSnakeLine(HorizontalSubstationLayout.java:36)
	at com.powsybl.sld.layout.AbstractLayout.manageSnakeLines(AbstractLayout.java:55)
	at com.powsybl.sld.layout.HorizontalSubstationLayout.manageSnakeLines(HorizontalSubstationLayout.java:72)
	at com.powsybl.sld.layout.AbstractSubstationLayout.run(AbstractSubstationLayout.java:37)
	at com.powsybl.sld.AbstractTestCase.substationGraphLayout(AbstractTestCase.java:251)
	at com.powsybl.sld.raw.TestCase11SubstationGraph.testH(TestCase11SubstationGraph.java:294)

### Extra Information

_No response_
