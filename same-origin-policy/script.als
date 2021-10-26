module script

open browser

abstract sig Script extends Client{context: Document}

fact Wellformedness
{
    no disj s1, s2: Script | s1.context = s2.context
}

fun browser[s: Script, t: Time]: Browser {(documents.t).(s.context)}

sig XmlHttpRequest extends HttpRequest {}
{
    from in Script
    let b = from.browser[start] |
        sentCookies in b.cookies.start and matchingScope[sentCookies, url]
    noBrowserChange[start, end] and noDocumentChange[start, end]
}

abstract sig BrowserOp extends Call {doc: Document}
{
    from in Script and to in Browser
    doc + from.context in to.documents.start
    noBrowserChange[start, end]
}

sig ReadDom extends BrowserOp {result: Resource}
{
    result = doc.content.start
    noDocumentChange[start, end]
}

sig WriteDom extends BrowserOp {newDom: Resource}
{
    content.end = content.start ++ doc -> newDom
    domain.end = domain.start
}

abstract sig EventHandler extends Call
{
    causedBy: Call
}{
    lt[causedBy.@start, start]
    from in Browser and to in Script
    from in causedBy.@to + causedBy.@from
    to.context in from.documents.start
    noDocumentChange[start, end]
    noBrowserChange[start, end]
}

pred noBrowserChange[start, end: Time]
{
    documents.end = documents.start and cookies.end = cookies.start
}

pred noDocumentChange[start, end: Time]
{
    content.end = content.start and domain.end = domain.start
}

run {} for 3
