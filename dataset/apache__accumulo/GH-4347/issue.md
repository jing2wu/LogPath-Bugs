# Generate Splits produces malformed output

- Issue: https://github.com/apache/accumulo/issues/4347
- Opened by ddanielr on 2024-03-07, closed on 2024-03-20
- Labels: bug
- Fix commit: 92331ea113b12c0a833a0a5ea714294832c6d822

## Report

**Describe the bug**
The `./accumulo generate-splits` utility is a useful way to generate split points on-demand. 
generate-splits will write its output to stdout or to a file and supports base64 encoding. 

However, when the utility encounters what it determines to be non-printable characters, it removes them from its output and 
logs a `debug` message.
https://github.com/apache/accumulo/blob/f3d5fb01d701a6932d37d2f67f52cc0eefa64d50/core/src/main/java/org/apache/accumulo/core/file/rfile/GenerateSplits.java#L259-L271

Because generate splits still returns output, users expect that the output is correct and will only catch the error on manual comparison or on applying the new splits to a live system. 

**Versions (OS, Maven, Java, and others, as appropriate):**
 - Affected version(s) of this project: 2.1.x

**To Reproduce**
Steps to reproduce the behavior (or a link to an example repository that reproduces the problem):
1. Create a table and write rows with null characters in the row id `"row\01"`
2. Use `./accumulo generate-splits` to generate split points for that table
3. Compare the output from generate-splits to the actual row IDs in the table, notice that they don't line up.

**Expected behavior**
If the output to the user is malformed then the utility should throw an error unless a user has provided an override.

**Additional context**
I did not confirm this, but my expectation is that the debug log message would not be created unless the log4j2 level was set to debug. 
https://github.com/apache/accumulo/blob/efdc4fc3d725d9bb2c364db6548c9251ea793a6d/assemble/conf/log4j2-service.properties#L79

This is additionally problematic as there's a good chance this logging level has been decreased on production systems to reduce log file sizes.

## Comment by DomGarguilo on 2024-03-18

It looks like the code in 2.1 might be functioning how you are proposing it should function already:
https://github.com/apache/accumulo/blob/f3e75f0e46a320d10f222546c33ada896c371e7c/core/src/main/java/org/apache/accumulo/core/file/rfile/GenerateSplits.java#L280-L290
Which differs from the code you referenced above which does not throw an exception. If I am interpreting this correctly, I am wondering what the reason behind going from throwing an exception in 2.1 to logging in main. Either way, maybe this ticket only applies to main and up.

## Comment by ddanielr on 2024-03-20

@DomGarguilo My Bad, this is still open due to a case of poor ticket linking.  #4348 was already merged in to fix this issue. 

Confirmed that the fix was originally merged into 2.1 and has been merged into main and elasticity branches as well.
Ticket has been completed.
