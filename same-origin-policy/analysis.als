module analysis
open flow

sig TrustedModule, MaliciousModule in DataflowModule {}
sig CriticalData, MaliciousData in Data {}

assert Confidentiality
{
    no m: DataflowModule - TrustedModule, t: Time |
        some CriticalData & m.accesses.t
}

assert Integrity
{
    no u: TrustedModule, t: Time |
        some MaliciousData & u.accesses.t
}

fact
{
    no m: MaliciousModule | some CriticalData & m.accesses.init
    no m: TrustedModule | some MaliciousData & m.accesses.init
    no TrustedModule & MaliciousModule
    DataflowModule = TrustedModule + MaliciousModule
    no CriticalData & MaliciousData
}

check Confidentiality for 3
check Integrity for 3
