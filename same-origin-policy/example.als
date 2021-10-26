module example
open analysis

one sig EmailServer extends Server {}
one sig InboxPage extends Document {}
{
    domain.init = EmailDomain
    content.init = MyInboxInfo
}
one sig InboxScript extends Script {}{context = InboxPage}

one sig CalendarServer extends Server {}
one sig CalendarPage extends Document {}
{
    domain.init = CalendarDomain
    content.init = MySchedule
}
one sig CalendarScript extends Script {}{context = CalendarPage}

one sig BlogServer extends Server {}
one sig BlogPage extends Document {}{domain.init = BlogDomain}

one sig EmailDomain, CalendarDomain, BlogDomain extends Domain {}
one sig ExampleDomain extends Domain {}
{
    subsumes = EmailDomain + CalendarDomain + BlogDomain + this
}

one sig EvilServer extends Server {}
one sig AdBanner extends Document {}
{
    domain.init = EvilDomain
    no CriticalData & content.init
}
one sig EvilScript extends Script {}
one sig EvilDomain extends Domain {}

one sig MyBrowser extends Browser {}
one sig MyInboxInfo in Resource {}
one sig MySchedule in Resource {}
one sig MyCookie in Cookie {}{domains = EmailDomain + CalendarDomain}

one sig HTTP extends Protocol {}

sig GetInboxInfo in HttpRequest {}
{
    to in EmailServer
    MyCookie in sentCookies
}

sig GetSchedule in HttpRequest {}
{
    to in CalendarServer
    MyCookie in sentCookies
}

fact SecurityAssumptions
{
    EmailServer + MyBrowser + CalendarServer +
        InboxScript + CalendarScript + BlogServer in TrustedModule
    EvilScript + EvilServer in MaliciousModule
    CriticalData = MyInboxInfo + MyCookie + MySchedule
        no initData[MaliciousModule] & CriticalData
        no initData[TrustedModule] & MaliciousData
    Dns.map = EmailDomain -> EmailServer + CalendarDomain -> CalendarServer
        + BlogDomain -> BlogServer + EvilDomain -> EvilServer
    MyInboxInfo != MySchedule
}

fun currentCall: Call -> Time
{
    {c: Call, t: Time | c.start = t}
}
fun relevantModules: DataflowModule -> Time
{
    {m: DataflowModule, t: Time | m in currentCall.t.(from + to)}
}

run {} for 3
