# Care-Gaps Concurrent modification exception

- Issue: https://github.com/cqframework/clinical-reasoning/issues/466
- Opened by Capt-Mac on 2024-05-29, closed on 2024-06-11
- Labels: bug, dQM
- Fix commit: 862b4b1fa2494f6c5891b080566e16e54a19b713

## Report

There is a bug in this [method](https://github.com/cqframework/clinical-reasoning/blob/ae83f7114f756e7da32ac6e84c95883b265ac545/cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/measure/r4/R4CareGapsService.java#L321C5-L333C6) that causes Measures that only specify scoring on the group level or are missing an improvement notation on the measure resource to throw an exception.

Steps:
1. POST Measure: [ecqm-content-qicore-2024/bundles/measure/ColonCancerScreeningFHIR/ColonCancerScreeningFHIR-bundle.json at main · cqframework/ecqm-content-qicore-2024](https://github.com/cqframework/ecqm-content-qicore-2024/blob/main/bundles/measure/ColonCancerScreeningFHIR/ColonCancerScreeningFHIR-bundle.json) 
4. POST Data: [ecqm-content-qicore-2024/bundles/measure/ColonCancerScreeningFHIR/ColonCancerScreeningFHIR-files/tests-bf3f2c9a-a802-4522-8e38-d1c806e71483-bundle.json at main · cqframework/ecqm-content-qicore-2024](https://github.com/cqframework/ecqm-content-qicore-2024/blob/main/bundles/measure/ColonCancerScreeningFHIR/ColonCancerScreeningFHIR-files/tests-bf3f2c9a-a802-4522-8e38-d1c806e71483-bundle.json)

5. run `http://localhost:8000/Measure/$care-gaps?periodStart=2025-01-01&periodEnd=2025-12-31&subject=Patient/bf3f2c9a-a802-4522-8e38-d1c806e71483&status=closed-gap&status=open-gap&measureId=ColonCancerScreeningFHIR` 

Observed Results 
 ```{
"resourceType": "OperationOutcome",
"issue": [ {
"severity": "error",
"code": "processing",
"diagnostics": "HAPI-0389: Failed to call access method: java.util.ConcurrentModificationException"
} ]
}```

Expected results

Care-Gaps report with no error
