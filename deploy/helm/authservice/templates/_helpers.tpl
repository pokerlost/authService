{{- define "authservice.name" -}}
authservice
{{- end }}

{{- define "authservice.fullname" -}}
{{ .Release.Name }}-authservice
{{- end }}

{{- define "authservice.labels" -}}
app.kubernetes.io/name: {{ include "authservice.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end }}

{{- define "authservice.selectorLabels" -}}
app.kubernetes.io/name: {{ include "authservice.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
