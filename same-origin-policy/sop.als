module sop
open browser
open cors
open origin
open setDomain

fact sameOriginPolicy
{
    domSop
    xmlHttpReqSop
}

pred domSop
{
    all o: ReadDom + WriteDom | let target = o.doc, caller = o.from.context |
        origin[target] = origin[caller] or
        (target + caller in (o.prevs <: SetDomain).doc and
            currOrigin[target, o.start] = currOrigin[caller, o.start])
}

pred xmlHttpReqSop
{
    all x: XmlHttpRequest |
        origin[x.url] = origin[x.from.context.src] or
        x in CorsRequest
}

run {some c: ReadDom + WriteDom | origin[c.doc.src] != origin[c.from.context.src]} for 4
