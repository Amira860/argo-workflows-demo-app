package main

deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.containers[0].resources.requests.cpu
  msg := "containers must declare cpu requests"
}

deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.containers[0].resources.requests.memory
  msg := "containers must declare memory requests"
}

deny[msg] {
  input.kind == "Deployment"
  endswith(input.spec.template.spec.containers[0].image, ":latest")
  msg := "container image must not use latest tag"
}

deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.containers[0].readinessProbe
  msg := "containers must declare readiness probes"
}
