# Manual native compaction OOM with wide intervals

- Issue: https://github.com/apache/druid/issues/19117
- Opened by gianm on 2026-03-09, closed on 2026-03-11
- Labels: Bug
- Fix commit: ad1b5f28bfecfd7b3cbd7f86d0d03c0af61df9b8

## Report

Since #18950, native compaction tasks can OOM due to excessive memory usage in `CachingLocalSegmentAllocator` when the compaction spec uses hash partitioning with a very wide interval, like `0000/9999`. I think this will only happen with manual compaction, since with autocompaction, the interval is generally targeted to the segments we actually want to compact.

The issue stems from a change in logic in `CompactionTask#createDataSchemasForIntervals`. Prior to the PR, the interval for the `DataSchema` was determined based solely on the segments actually being processed. Afterwards, it's extended to the umbrella interval of those segments and the user-provided job interval. The relevant change is at: https://github.com/apache/druid/pull/18950/changes#diff-ddc42134e9e789d2b0af5db8c313abd3026f99a919ae26b6137c663f6f2d5228L638-L643

As an effect of this change, the `HashPartitionAnalysis` will contain an entry for every day in the user-supplied interval. That in turn leads the `CachingLocalSegmentAllocator` to generate buckets and shard specs for all possible days.

I don't think the MSQ runner would have a problem like this, because the equivalent MSQ statement (like the following SQL) would not attempt to create buckets for all 3.6 million days. It would only process day buckets that actually contained data. Then it would check to see if any tombstones need to be created, and created any needed ones. Critically, it will only create tombstones for day buckets that actually have both (1) some input data and (2) no output data. This happens in `ControllerImpl#findIntervalsToDrop`.

```
REPLACE INTO tbl
OVERWRITE WHERE __time >= TIMESTAMP '0001-01-01 00:00:00' AND __time < TIMESTAMP '9999-01-01 00:00:00'
SELECT * FROM tbl
PARTITIONED BY DAY
```

## Comment by gianm on 2026-03-09

Perhaps the simplest fix is to go back to the old behavior: set the data schema interval to the segment intervals only. The thread at https://github.com/apache/druid/pull/18950/changes#r2757718584 references an offline conversation about why we needed to make the change.

@cecemei @kfaraz do you recall what the reason was? I wonder if it would be fine to revert it to be the umbrella interval of `timelineSegments`. I would suppose that the umbrella interval of `timelineSegments` would by definition include the full segment intervals, so should take care of any partial overlap.

## Comment by kfaraz on 2026-03-10

@gianm , the discussion here https://github.com/apache/druid/pull/18950#discussion_r2757715069 has some details.

> ah i was thinking the case when the umbrella interval is smaller than the original interval (which is the case in CompactionTaskRunBase, the segment is hourly and there's only segments in hour 0 - hour 3, so compaction task only locks for 3 hours, but the interval can be all day (see NativeCompactionTaskRunTest). MSQ runner failed when getting a task lock with the following change:

Essentially, if a `compact` task is trying to compact a DAY interval but that interval currently contains only a couple of HOUR segments, we would end up locking an interval smaller than the whole DAY unless we consider the `segmentProvider.interval` as well. This would mean that other tasks could potentially write concurrently to the remainer of the DAY interval, even though we had intended to lock the whole thing up.

A solution to the large number of intervals (since we have encountered this issue earlier as well) could be to impose a limit on `Granularity.getIterable()` or at least have a safe variant of that method which imposes a limit on the number of intervals created. If that number is exceeded, we could throw an exception, and advise the user to either choose a smaller interval or a bigger granularity.

## Comment by gianm on 2026-03-10

That provides a reason why the lock interval should be wider, but why does the data schema interval need to match the lock interval? It should be ok for it to be a smaller interval, as long as it's fully contained by the lock.

As to solving it by limiting the number of buckets, that could he a last resort, but it's not ideal because these long intervals did used to work with the native runner.

## Comment by gianm on 2026-03-10

Maybe the data schema interval just needs to be the umbrella of the time segment intervals, rounded out to the segment granularity, to cover this hour -> day case, rather than expanded to the entire lock interval. (Then check that the rounded interval fits within the lock and throw if it doesn't)

## Comment by kfaraz on 2026-03-10

Yes, @gianm , that's true, the data schema interval can still be just the umbrella interval. We just need the lock to cover the whole interval.

@cecemei , would that solve the use case that you had encountered? Or are we missing some corner case.

## Comment by cecemei on 2026-03-10

true it should not affect the data schema interval, fixing this in #19121.
