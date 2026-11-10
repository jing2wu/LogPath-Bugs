# DelphiCoverageSensor case sensitivity issue

- Issue: https://github.com/integrated-application-development/sonar-delphi/issues/325
- Opened by simonegirlanda on 2024-12-11, closed on 2024-12-17
- Labels: bug
- Fix commit: 223a6c32e27e99c7b86078a66aaab51b587d6c3e

## Report

### Prerequisites

- [X] This question has not already been answered.
- [X] This question is about SonarDelphi, not SonarQube or Delphi.

### Inquiry

In SonarQube coverage analysis of our Delphi project we are getting many errors (>100) for "File not found in project", so that these files are not included in the coverage analysis. 

```
00:13:53.976 INFO  Sensor DelphiSensor [communitydelphi] (done) | time=682841ms
00:13:53.976 INFO  Sensor DelphiCoverageSensor [communitydelphi]
00:13:53.976 INFO  Adding coverage reports.
00:13:53.982 INFO  Parsing coverage report: _CodeCoverageOutput2\CodeCoverage_Summary.xml
.
.00:13:54.881 DEBUG Parsing line hit information for file: AnagListDataSet.pas
00:13:54.882 DEBUG File not found in project: anagNotifyEvent.pas
00:13:54.883 DEBUG File not found in project: anagrafica.pas
00:13:54.883 DEBUG Parsing line hit information for file: AnagraficaDataModule.pas
```

The file anagrafica.pas exist in our project and it is used by many other units, but the correct file name is "Anagrafica.pas".

in the DelphiCoverageOutput the file is present in lowercase:

```
 <package name="Anagrafica">
        <coverage type="class, %" value="14%   (5/36)"/>
        <coverage type="method, %" value="12%   (51/443)"/>
        <coverage type="block, %" value="11%   (707/6613)"/>
        <coverage type="line, %" value="11%   (707/6613)"/>
        <srcfile name="anagrafica.pas">
```

As far I've understood from DelphiCoverage sources its output is based on information contained the build Map file.
In the map file anagrafica.pas is referenced with the first letter in lower case:
```
Line numbers for GESTFORMULA(anagrafica.pas) segment .text

  2168 0001:039276F8  2169 0001:0392771F  2170 0001:03927729  2172 0001:03927741
```
I'm supposing that this depend on the way the unit is declared in the Uses and anagrafica is referenced in lowercase by 380 other files in our project.  

 :-(

In the GESTFORMULA unit anagrafica.pas is referenced with first character upper case (I'm confused...):
```

unit GESTFORMULA;

interface

uses
  Anagrafica, ....
```

For testing I've modified manually the Delphicoverage output setting the name for the file to "Anagrafica.pas" and this eliminate the coverage analysis problem.

```
11:28:34.210 INFO  Sensor DelphiSensor [communitydelphi] (done) | time=581338ms
11:28:34.210 INFO  Sensor DelphiCoverageSensor [communitydelphi]
11:28:34.211 INFO  Adding coverage reports.
11:28:34.216 INFO  Parsing coverage report: _CodeCoverageOutput2\CodeCoverage_Summary.xml
.
.
11:28:35.149 DEBUG Parsing line hit information for file: AnagListDataSet.pas
11:28:35.151 DEBUG File not found in project: anagNotifyEvent.pas
11:28:35.151 DEBUG Parsing line hit information for file: Anagrafica.pas
```


These are my questions:

1. can you change the DelphiCoverageSensor to use case-insensitive search for file in project?
2. can you show coverage analysis errors (file not found or any other) without activating debug option (-X) in SonarScanner?

## Comment by cirras on 2024-12-11

> can you change the DelphiCoverageSensor to use case-insensitive search for file in project?

We'll have a look! Thanks for reporting this flaw.

> can you show coverage analysis errors (file not found or any other) without activating debug option (-X) in SonarScanner?

I'd be hesitant to do this because the case of "file specified in coverage report but not included in sonar project" looks like it could be trivially triggered by excluding a source file in `sonar-project.properties`.

## Comment by fourls on 2024-12-12

> > can you show coverage analysis errors (file not found or any other) without activating debug option (-X) in SonarScanner?
> 
> I'd be hesitant to do this because the case of "file specified in coverage report but not included in sonar project" looks like it could be trivially triggered by excluding a source file in `sonar-project.properties`.

Thinking about it, this could also be trivially corrected by updating your DelphiCodeCoverage command to exclude the same source files (since you pass in each individual file you want covered).
