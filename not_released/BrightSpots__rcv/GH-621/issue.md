# NPE when tabulating by precinct

- Issue: https://github.com/BrightSpots/rcv/issues/621
- Opened by chughes297 on 2022-09-12, closed on 2023-06-09
- Labels: bug
- Fix commit: a8308e8614c332815b83ae45422b16c39e6649cd

## Report

I'm trying to run the Alaska CVR through RCTab right now but keep getting an NPE. 

Here's the error message: 

> java.lang.NullPointerException: Cannot invoke "network.brightspots.rcv.TallyTransfers.addTransfer(int, String, String, java.math.BigDecimal)" because the return value of "java.util.Map.get(Object)" is null

For good measure I checked if this happens on both 1.2.0 and 1.3.0 - it does. I had never previously gotten this error on 1.2.0. though. Makes me think it must be an issue with my computer specifically, but I can't figure out what the issue might be. I'm on macOS Monterey 12.5.1 on a 2020 MacBook Air. 

Here's more of the log before I get that error:

> 2022-09-12 12:54:58 EDT INFO: Writing cast vote records in generic format to file: /Users/kazooiedog/Desktop/Hiding all the stuff on my desktop/RCVRC/RCV Legislation and Grassroots/Alaska/Results Check/2022-09-12_12-54-52_dominion_conversion_contest_69.csv...
> 2022-09-12 12:54:59 EDT INFO: Successfully wrote: /Users/kazooiedog/Desktop/Hiding all the stuff on my desktop/RCVRC/RCV Legislation and Grassroots/Alaska/Results Check/2022-09-12_12-54-52_dominion_conversion_contest_69.csv
> 2022-09-12 12:54:59 EDT INFO: Parsed 192289 cast vote records successfully.
> 2022-09-12 12:54:59 EDT INFO: There are 3 declared candidates for this contest:
> 2022-09-12 12:54:59 EDT INFO: 215
> 2022-09-12 12:54:59 EDT INFO: 217
> 2022-09-12 12:54:59 EDT INFO: 218
> 2022-09-12 12:54:59 EDT INFO: Round: 1
> 2022-09-12 12:54:59 EDT SEVERE: Error during tabulation:
> java.lang.NullPointerException: Cannot invoke "network.brightspots.rcv.TallyTransfers.addTransfer(int, String, String, java.math.BigDecimal)" because the return value of "java.util.Map.get(Object)" is null
> Tabulation failed!

Any ideas?

## Comment by tarheel on 2022-09-12

Hmm. I doubt it's your computer specifically. More likely it's an edge case that's exposing a bug in the code that we hadn't noticed previously.

Could you send me the config file and the CVR input, and when I have time I'll try to debug it?

## Comment by chughes297 on 2022-09-12

Hi for some reason my config file was the problem?? I just redid the config from the ground up and it worked.

## Comment by tarheel on 2022-09-12

Hmm. Do you still have the bad version of the config? Not as urgent to fix it, but I'd still like to figure out how it led to the NPE, since that really shouldn't ever happen.

## Comment by chughes297 on 2022-09-12

Managed to recreate the error, it's when I select "tabulate by precinct" that tabulation fails. Will email the config.

## Comment by artoonie on 2023-03-14

Can the config be uploaded here as well?

## Comment by rrojas350 on 2023-03-14

Here you go @artoonie. [Issue #621 AK Config and CVR](https://drive.google.com/drive/folders/1hVnuk5mhutYBZnQyH-NBe0nbV30k1BZt?usp=sharing)

## Comment by artoonie on 2023-04-03

I see this is in-progress by @tarheel -- just want to double-check that's the case? Let me know if this is a task I should take on, and I'll re-assign it to me. Don't want to duplicate any in-progress work.

## Comment by tarheel on 2023-04-03

Feel free to grab it; I haven't started it.

## Comment by artoonie on 2023-04-04

Would love feedback on #650 -- I'm not sure what the best path forward is here. At the heart of my confusion is a lack of knowledge about the difference between "Precinct" and "Precinct Portion".

Summary of what was wrong:
1. This file doesn't have any precinct data, only precinct portion data.
2. Further, dominion data never copied over precinct data.
3. Precincts with zero votes led to an exception

The bug is reproducible with all dominion data I have tested when tabulating by precinct.

Summary of fixes are commented inline in the pull request draft.
