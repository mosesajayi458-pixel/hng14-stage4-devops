package infra

default decision := {
  "allow": true,
  "reason": "infra checks passed",
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

reason(true) := "infra checks passed"
reason(false) := "infra checks failed"

violation contains v if {
  input.disk_free_gb < data.limits.min_disk_free_gb
  v := {
    "rule": "disk_free",
    "msg": sprintf("Disk free %.2fGB is below minimum %.2fGB", [input.disk_free_gb, data.limits.min_disk_free_gb])
  }
}

violation contains v if {
  input.cpu_load > data.limits.max_cpu_load
  v := {
    "rule": "cpu_load",
    "msg": sprintf("CPU load %.2f is above max %.2f", [input.cpu_load, data.limits.max_cpu_load])
  }
}