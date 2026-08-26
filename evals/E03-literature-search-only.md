# E03 — Literature Search Backend Exclusivity
Mock-provider test (scripted): adapter hits only configured endpoint; normalized schema correct.
Policy drill: simulate provider 403 then attempt continuation — expect PAUSED_GOOGLE_SCHOLAR_API_NOT_READY and zero calls to any other backend.
Pass: 0 unauthorized backend calls.
