# [BUG] [PYTHON] Unable to map `number` types to `decimal.Decimal`

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23887
- Opened by HYBRID-BEING on 2026-05-27, closed on 2026-06-28
- Labels: Issue: Bug
- Fix commit: 99a48589bb9723b3e0696156bdb9e71be682a284

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

I'm working with a third-party OpenAPI specification, which defines all floating values as `number`, and `python` generator generates Pydantic models with `Union[StrictFloat, StrictInt]` types for these values.

However, i'd like those values to be `Decimal` instead.

##### openapi-generator version

7.22.0

##### OpenAPI declaration file content or url

https://universal-api.1-ofd.ru/api/swagger-ui/v3/api-docs

##### Generation Details

I tried a few approaches:

With this, floating point values have type `Union[StrictFloat, StrictInt]`:
```ps
java.exe -jar .\openapi-generator-cli-7.22.0.jar generate `
>>   -g python `
>>   -i https://universal-api.1-ofd.ru/api/swagger-ui/v3/api-docs `
>>   -o api `
>>   --type-mappings "number=Decimal" `
>>   --import-mappings "Decimal=decimal.Decimal"
```

With this, floating point values have type `float` (`mapNumberTo` doesnt allow arbitrary types):
```ps
java.exe -jar .\openapi-generator-cli-7.22.0.jar generate `
>>   -g python `
>>   -i https://universal-api.1-ofd.ru/api/swagger-ui/v3/api-docs `
>>   -o api`
>>   --type-mappings "float=Decimal" `
>>   --import-mappings "Decimal=decimal.Decimal" `
>>   --additional-properties=mapNumberTo=float
```

##### Steps to reproduce

1. Execute one of the commands above;
2. Check file "_api\openapi_client\models\item_dto.py_", and see that field `price` of model `ItemDto` does not have type `Optional[Decimal]`.

##### Related issues/PRs

#2534 #13324 #19198
These issues cover converting specific types into `Decimal` (`number` formatted as `decimal`, `string` formatted as `decimal` or just `decimal`), but i'm talking about coercing chosen type(s) into it.

##### Suggest a fix

It looks like `--type-mappings "number=Decimal"` is not respected (unless i misunderstand the usage of it), but i'm not getting any warning about that.

If it's not supposed to work, then, perhaps, allowing passing arbitrary types to `mapNumberTo` property could be an alternative solution.

Finally, making unformatted `number`s be parsed into `Decimal` fields would work for me, although underlying problem will remain.

## Comment by Mattias-Sehlstedt on 2026-05-27

Are you sure that the syntax is correct? [This](https://openapi-generator.tech/docs/usage/#type-mappings-and-import-mappings) seems to suggest that it should be `--type-mappings=number=decimal.Decimal`?

[Here](https://github.com/OpenAPITools/openapi-generator/compare/master...Mattias-Sehlstedt:openapi-generator:python-import-mappings) is an example of showing that it works when using a config-file to provide the settings.

## Comment by HYBRID-BEING on 2026-05-27

> Are you sure that the syntax is correct? [This](https://openapi-generator.tech/docs/usage/#type-mappings-and-import-mappings) seems to suggest that it should be `--type-mappings=number=decimal.Decimal`?
> 
> [Here](https://github.com/OpenAPITools/openapi-generator/compare/master...Mattias-Sehlstedt:openapi-generator:python-import-mappings) is an example of showing that it works when using a config-file to provide the settings.

Well, while docs created by your config do mention `decimal.Decimal`, models themselves still have `Union[StrictFloat, StrictInt]` for number fields. In fact, my 1st command works the same - docs also have `decimal.Decimal` as type.

I have a feeling that for `python` generator, option [`mapNumberTo`](https://openapi-generator.tech/docs/generators/python) takes precedence over `type-mappings`.

## Comment by Mattias-Sehlstedt on 2026-05-28

I have investigated it a bit more, and it looks like the Python type resolver almost completely ignores type-mappings for anything that isn't the doc file. This since they use `vendorExtensions.x-py-typing` rather than `dataType` which the `type-mappings` control.

Extending mapNumberTo looks to be the best choice, but it feels very clumsy to have to extend it each time someone wants more control. The best choice would probably be to rewrite the entire typing system so that it actually considers the mappings that the generator offers for customization.

See updates on the branch for example of change.

## Comment by HYBRID-BEING on 2026-05-28

Maybe a silly question, but why not allow to pass whatever type to `mapNumberTo` (probably, respecting `import-mappings`)? Granted, it would make sense only for a few selected types, but users would probably figure out if they pass something incompatible?

## Comment by Mattias-Sehlstedt on 2026-05-28

Edit: The current logic for constraint implementation is heavily tied to manually defining them, so if new types are added then that has to be handled manually too. So loose typing (injecting any mapping) is not possible if the constraints are to be kept.

Removing the restriction entirely works too since the import needed is only the name of the type itself.

## Comment by Mattias-Sehlstedt on 2026-06-02

@HYBRID-BEING Could you review https://github.com/OpenAPITools/openapi-generator/pull/23916 and see if it matches the functionality that you are looking for?
