package canary

default decision := {
  "allow": true,
  "reason": "canary checks passed",
  "violations": []
}

decision := output if {
  violations := [v | v := violation[_]]
  allow := count(violations) == 0

  output := {
    "allow": allow,
    "reason": reason(allow),
    "violations": violations
  }
}

reason(true) := "canary checks passed"
reason(false) := "canary checks failed"

violation contains v if {
  input.error_rate > data.limits.max_error_rate
  v := {
    "rule": "error_rate",
    "msg": sprintf("Error rate %.4f is above max %.4f", [input.error_rate, data.limits.max_error_rate])
  }
}

violation contains v if {
  input.p99_latency_ms > data.limits.max_p99_latency_ms
  v := {
    "rule": "p99_latency",
    "msg": sprintf("P99 latency %.2fms is above max %.2fms", [input.p99_latency_ms, data.limits.max_p99_latency_ms])
  }
}