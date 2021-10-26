module browser
open http

abstract sig Document
{
    src: Url,
    content: Resource -> Time,
    domain: Domain -> Time,
}

abstract sig Browser extends Client
{
    documents: Document -> Time,
    cookies: Cookie -> Time,
}

fact Wellformedness
{
    no disj b1, b2: Browser, t: Time | some b1.documents.t & b2.documents.t
    all b: Browser, d: b.documents.init | d.src.host = d.domain.init
}

sig BrowserHttpRequest extends HttpRequest {doc: lone Document}
{
    from in Browser
    sentCookies in from.cookies.start
    matchingScope[sentCookies, url]

    some doc iff some response
    documents.end = documents.start + from -> doc
    content.end = content.start ++ doc -> response
    domain.end = domain.start ++ doc -> url.host
    some doc implies doc.src = url

    cookies.end = cookies.start + from -> sentCookies
}

pred matchingScope[cookies: set Cookie, url: Url]
{
    all c: cookies | url.host in c.domains
}

check
{
    no disj d1, d2: Document | some t: Time | d1.src not in d2.src and d1.domain.t = d2.domain.t
}
