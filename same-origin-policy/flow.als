module flow
open jsonp
open postMessage
open setDomain
open cors
open sop

sig Data in Resource + Cookie {}

sig DataflowCall extends Call
{
    args, returns: set Data,
}{
    args in from.accesses.start +
        (this in XmlHttpRequest implies from.browser[start].accesses.start & Cookie else none)

    returns in to.accesses.start

    this in HttpRequest implies
        args = this.sentCookies + this.body and
        returns = this.receivedCookies + this.response + this.response.payload

    this in ReadDom implies no args and returns = this.result
    this in WriteDom implies args = this.newDom and no returns
    this in SetDomain implies no args + returns
    this in PostMessage implies args = this.message and no returns

    this in ExecCallback implies args = this.payload and no returns
    this in ReceiveMessage implies args = this.data and no returns
}

sig DataflowModule in Endpoint
{
    accesses: Data -> Time,
}{
    all d: Data, t: Time - first |
        d -> t in accesses implies
            d -> t.prev in accesses or
            some c: Call & end.t |
                c.to = this and d in c.args or
                c.from = this and d in c.returns

    this in Server implies Path.(this.resources) in initData
}

fact {Call in DataflowCall and Endpoint in DataflowModule}
fun initData[m: DataflowModule]: set Data{m.accesses.first}

run {some Client.accesses} for 3
