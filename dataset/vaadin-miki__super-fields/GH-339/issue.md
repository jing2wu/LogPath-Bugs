# Setting fraction/integer digits should not be destructive

- Issue: https://github.com/vaadin-miki/super-fields/issues/339
- Opened by vaadin-miki on 2022-01-10, closed on 2022-01-11
- Labels: bug
- Fix commit: 56f5b80660b18da58d2c6548c458a56e7216945d

## Report

Modifying fraction/integer digits should not be destructive to the value of the field.

Introduced as a side effect of implementing #337 - reported there as not wanted.

## Comment by weiliang2 on 2022-01-10

Hello,

really appreciate your effort to look into this. Hope to hear some good news.

## Comment by vaadin-miki on 2022-01-11

@weiliang2 according to the tests those changes should now no longer be destructive - will do my best to make a new release this week (or early next week)
