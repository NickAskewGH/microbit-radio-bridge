# Radio captures

Store raw, immutable capture sessions by protocol family. For each session,
include metadata recording hardware, firmware revision, timestamp, remote and
vehicle identity, control action, RF settings, and whether the vehicle was
powered or safely isolated.

Promote minimal, reviewed packets into `protocols/<name>/fixtures/` for automated
decoder and encoder tests. Do not edit raw captures to fit a protocol hypothesis.