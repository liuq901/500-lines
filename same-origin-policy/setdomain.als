module setDomain
open script

sig SetDomain extends BrowserOp{newDomain: Domain}
{
    doc = from.context
    domain.end = domain.start ++ doc -> newDomain
    content.end = content.start
}

fact setDomainRule
{
    all d: Document | d.src.host in (d.domain.Time).subsumes
}

run {some sd: SetDomain | sd.doc.src.host != sd.newDomain}

run
{
    some SetDomain
    all sd: SetDomain | sd.doc.src.host != sd.newDomain
    no d: Domain | some d.subsumes
}
