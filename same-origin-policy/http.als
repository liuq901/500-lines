module http
open call[Endpoint]
open util/relation

abstract sig Resource {}
abstract sig Endpoint {}

abstract sig Protocol, Port, Path {}
sig Domain {subsumes: set Domain}
fact subsumesRule {partialOrder[subsumes, Domain]}

sig Url
{
    protocol: Protocol,
    host: Domain,
    port: lone Port,
    path: Path,
}

abstract sig HttpRequest extends Call
{
    url: Url,
    sentCookies: set Cookie,
    body: lone Resource,
    receivedCookies: set Cookie,
    response: lone Resource,
}{
    from in Client
    to in Dns.map[url.host]
    all c: receivedCookies | url.host in c.domains
    response = to.resources[url.path]
}

abstract sig Client extends Endpoint {}
abstract sig Server extends Endpoint {resources: Path -> lone Resource}

fact ServerAssumption
{
    all s1, s2: Server | (some Dns.map.s1 & Dns.map.s2) implies s1.resources = s2.resources
}

sig Cookie {domains: set Domain}

one sig Dns{map: Domain -> Server}

run {} for 3

run {all r: HttpRequest | some r.receivedCookies} for 3

check {all r: HttpRequest | r.url.path in r.to.resources.Resource} for 3

check {all d: Domain | no disj s1, s2: Server | s1 + s2 in Dns.map[d]} for 3

check {all r1, r2: HttpRequest | r1.url = r2.url implies r1.response = r2.response} for 3
