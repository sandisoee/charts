{{/* vim: set filetype=mustache: */}}
{{/*
Kubernetes standard labels
*/}}
{{- define "moja.common.labels.standard" -}}
app.kubernetes.io/name: {{ include "moja.common.names.name" . }}
helm.sh/chart: {{ include "moja.common.names.chart" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Labels to use on deploy.spec.selector.matchLabels and svc.spec.selector
*/}}
{{- define "moja.common.labels.matchLabels" -}}
app.kubernetes.io/name: {{ include "moja.common.names.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
