param(
    [ValidateSet('dev','test','staging','prod','canary','green')]
    [string]$Overlay = 'dev'
)

kubectl kustomize "k8s/overlays/$Overlay"
