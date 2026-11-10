# Is the documentation for page number formatting correct?

- Issue: https://github.com/drmacro/wordinator/issues/116
- Opened by gkholman on 2023-02-26, closed on 2026-10-11
- Labels: bug
- Fix commit: 15ca712f105a1b9d0618f05909d0bfc39f33a121

## Report

In the schema I read:
````
        <attribute name="xslt-format">
          <a:documentation>
            <p>Number format as for the XSLT format attribute on the xsl:number instruction.
            This attribute must be specified if @format has the value "custom". If this attribute is
            specified and no value for @format is specified, @format is set to "custom".</p>
          </a:documentation>
        </attribute>
````

In the test: [page-number-format-20230226.zip](https://github.com/drmacro/wordinator/files/10834228/page-number-format-20230226.zip) I have:

````
<?xml version="1.0" encoding="UTF-8"?>
<wp:document xmlns:wp="urn:ns:wordinator:simplewpml">
  <wp:body>
    <wp:section type="nextPage">
      <wp:page-sequence-properties>
        <wp:page-number-properties start="1" format="custom" xslt-format="i"/>
        <wp:headers-and-footers>
          <wp:header>
            <wp:p style="Normal">
              <wp:page-number-ref/>
            </wp:p>
          </wp:header>
        </wp:headers-and-footers>
        <wp:page-size orient="portrait" width="210mm" height="297mm"/>
      </wp:page-sequence-properties>
      <wp:body>
        <wp:p><wp:run>This is the first page numbered in Roman lower-case</wp:run></wp:p>
      </wp:body>
    </wp:section>
    <wp:section type="nextPage">
      <wp:page-sequence-properties>
        <wp:page-number-properties start="1" format="custom" xslt-format="1"/>
        <wp:headers-and-footers>
          <wp:header>
            <wp:p style="Normal">
              <wp:page-number-ref/>
            </wp:p>
          </wp:header>
        </wp:headers-and-footers>
        <wp:page-size orient="portrait" width="210mm" height="297mm"/>
      </wp:page-sequence-properties>
      <wp:body>
        <wp:p><wp:run>This is the first page numbered in decimal</wp:run></wp:p>
      </wp:body>
    </wp:section>
  </wp:body>
</wp:document>
````

and yet I'm getting in the console report:

````
~/t/page-number-format-20230226 $ wordinator.sh . simple.dotx 
+ 2023-02-26 11:58:59,329 [INFO ] Input document or directory='.'
+ 2023-02-26 11:58:59,331 [INFO ] Output directory           ='.'
+ 2023-02-26 11:58:59,331 [INFO ] DOTX template              ='simple.dotx'
+ 2023-02-26 11:58:59,331 [INFO ] XSLT template              =Not specified
+ 2023-02-26 11:58:59,331 [INFO ] Catalog                    =Not specified
+ 2023-02-26 11:58:59,331 [INFO ] Chunk level                ='root'
+ 2023-02-26 11:58:59,732 [INFO ] Generating DOCX file "/Users/admin/t/page-number-format-20230226/./page-number-format-20230226.docx"
+ 2023-02-26 11:58:59,793 [WARN ] Page number format "custom" not supported. Use Word-specific values. Using "decimal"
+ 2023-02-26 11:58:59,827 [WARN ] Page number format "custom" not supported. Use Word-specific values. Using "decimal"
+ 2023-02-26 11:58:59,972 [INFO ] DOCX file generated.
````

## Comment by larsga on 2023-03-01

The source code says:

```
            // FIXME: Implement translation from XSLT number format values to the equivalent Word
            // number formatting values.
```

so apparently the documentation is correct, but the code hasn't been written.

## Comment by larsga on 2023-03-01

I suspect the schema may be promising more than it can deliver here, because I'm not sure how to implement this in Word. The problem is that we're not running code inside Word, but simply generating OOXML, so supporting something that's not supported in OOXML seems difficult. But maybe I'm overlooking something.

## Comment by gkholman on 2023-03-01

I didn't mention in the ticket that I have worked around this already.
Sorry.

I left the ticket as an observation.


--
(Sent from my phone; please excuse any auto-corrupt issues)
Contact info, blog, articles, etc. http://www.CraneSoftwrights.com/g/ |
Check our site for free XML, XSLT, XSL-FO and UBL developer resources |
Streaming hands-on XSLT/XPath 2 training class @ US$125(5 hours free) |
Essays (UBL, XML, etc.) http://www.linkedin.com/today/author/gkholman |

On Wed, Mar 1, 2023, 10:19 Lars Marius Garshol, ***@***.***>
wrote:

> I suspect the schema may be promising more than it can deliver here,
> because I'm not sure how to implement this in Word. The problem is that
> we're not running code inside Word, but simply generating OOXML, so
> supporting something that's not supported in OOXML seems difficult. But
> maybe I'm overlooking something.
>
> —
> Reply to this email directly, view it on GitHub
> <https://github.com/drmacro/wordinator/issues/116#issuecomment-1450326252>,
> or unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AAKCGXO2FYEBEGD4YZLLNNDWZ5SIRANCNFSM6AAAAAAVISD3L4>
> .
> You are receiving this because you authored the thread.Message ID:
> ***@***.***>
>

## Comment by larsga on 2023-03-01

No problem! I think this one is for Eliot to decide what he wants to do with. At least now I understand the issue.

## Comment by ekimbernow on 2026-10-11

Implemented in #198. `@xslt-format` tokens `1`, `01`, `a`, `A`, `i`, `I` now map to the equivalent Word page number formats. Word page numbers allow only a single numbering token, so prefix/suffix text (e.g. `1.`) is dropped with a warning, and unsupported tokens fall back to decimal with a warning.
