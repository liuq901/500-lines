module call[T]
open util/ordering[Time] as ord

sig Time {}
abstract sig Call
{
    start, end: Time,
    from, to: T,
}
fun init: Time {first}

fun prevs[c: Call]: set Call {{c': Call | c'.start in c.start.prevs}}

fact
{
    all t: Time - ord/last | some c: Call | c.start = t and c.end = t.next
    all c: Call | c.end = (c.start).next
}
