# Data Type Conversion Issue

- Issue: https://github.com/atlasmap/atlasmap/issues/3549
- Opened by Shrishti1234 on 2021-12-06, closed on 2021-12-07
- Labels: group/runtime, cat/bug
- Fix commit: a74a4bab14ebd78dd02f10f9f54425bb2136ad67

## Report

**Describe the bug**
Hi, I am facing one issue on runtime while doing transformation. I want to transform json to xml using atlasmap. I have created one mapping file which I am attaching for your reference.
There are two scenarios one positive and negative.
positive scenario: When I give all all objects(paramString , paramBoolean, paramDatetime) in JSON request it works fine as expected.
negative scenarios: When I removed one of object say "paramBoolean" or "paramDatetime" object then I am getting an error for which I have attached "error1.png" and "error2.png" in error folder of zip file.
I have also attached JSON request for this error in error folder.


**Attach .adm file and source document examples**
I am attaching one zip file which have following document.
1. SourceDoc.json : This is the source document for json request which I used for creating mapping spec.
2. TargetDoc.xml : This is the target document for xml request.
3. mappingspec.adm : mapping file created by altasmap using soucre and target doc.
4. error folder : This error folder have two screen shots attached error1.png and error2.png which shows error that I get at runtime
    and JsonRequestError.json is json request for which I am getting this error.


**To Reproduce**
Steps to reproduce the behavior:
1. Use the mappingspec.adm file attached in zip folder for transformation
2.  Create one rest route which is accepting JSON request and do transformation using atlasmap.
3. Send the JsonRequestError.json request to this route which is attached in zip file , it will throw an error.


**Expected behavior**
When "paramBoolean" or "paramDatetime" object is not coming in request it should not throw an error.

[AtlasmapIssue.zip](https://github.com/atlasmap/atlasmap/files/7659078/AtlasmapIssue.zip)

## Comment by igarashitm on 2021-12-06

One thing to note while I'm looking into - you have multiple mappings to a same target field, e.g.  `/params/paramBoolean/fieldName` and `/params/paramDatetime/fieldName` to `/methodCall/params/param/value/struct/member<>/name`. This will conflict at the target side and which one is actually written to the target side is not guaranteed.
I thought it was banned in UI, maybe checking logic is not working as expected (#3554).

## Comment by Shrishti1234 on 2021-12-07

> One thing to note while I'm looking into - you have multiple mappings to a same target field, e.g. `/params/paramBoolean/fieldName` and `/params/paramDatetime/fieldName` to `/methodCall/params/param/value/struct/member<>/name`. This will conflict at the target side and which one is actually written to the target side is not guaranteed. I thought it was banned in UI, maybe checking logic is not working as expected (#3554).

Hi @igarashitm,
I think this is not issue as I have mapped collection to collection and it is not creating an issue. Plz don't remove this feature as it full filling my requirement.
Why I have mapped multiple fieldName to name becuase every fieldName will create member tag as you can see from my TargetDoc.xml. I am attaching one zip file which have mapping spec for small use case and two screenshots.
1. mappingSpec.adm : mapping spec for transformation
2. SourceDoc : used as a source document for creating mapping.
3. TargetDoc : used as a target document for creating mapping.
4. positive case folder : This folder have one screenshot "positiveCase.png" which shows JSON request and their corresponding XML response which is also attached in same folder.
5. negative case folder : This folder have one screenshot "negativeScenarioExpectation.png". This is what I am expecting with this JSON request but I am getting an error. In this JSON request I have not given "paramDatetime" structure which is creating an issue and it is same for  "paramBoolean" .
[Atlasmap.zip](https://github.com/atlasmap/atlasmap/files/7666779/Atlasmap.zip)

## Comment by igarashitm on 2021-12-07

Ugh sorry I totally forgot we allowed that usecase - https://github.com/atlasmap/atlasmap/issues/2289
cf. #3554

## Comment by Shrishti1234 on 2021-12-08

> Ugh sorry I totally forgot we allowed that use case - #2289 cf. #3554 


Yes, This is the feature that I am currently using for my use case. But I am facing one issue, in mapping spec I have mapped all objects("paramString" , "paramBoolean". "paramDatetime") to target document and if I missed any one of the objects in request then it is throwing an error.
Can u tell me what exactly the cause of this error and how I can resolve that. The fix "NPE when an XML target collection is empty"  which you have done can resolve my problem or it is related to something else.
Please provide solution for this problem as this issue have blocked our use cases.

## Comment by igarashitm on 2021-12-08

#3555 fixed that issue.

## Comment by Shrishti1234 on 2021-12-08

> #3555 fixed that issue.

Thanks a lot @igarashitm, when I can get fixed Atlasmap jar as this is blocking our use case.

## Comment by igarashitm on 2021-12-08

https://github.com/atlasmap/atlasmap/releases/tag/atlasmap-2.3.3
