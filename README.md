# Backend For Navigo

[![Coverage](https://sonarqube.cs.ui.ac.id/api/project_badges/measure?project=navigo-ppl&metric=coverage&token=sqb_5375f89b9244ec43ddd9eeed2ecf29977bf97c52)](https://sonarqube.cs.ui.ac.id/dashboard?id=navigo-ppl)
[![Quality Gate Status](https://sonarqube.cs.ui.ac.id/api/project_badges/measure?project=navigo-ppl&metric=alert_status&token=sqb_5375f89b9244ec43ddd9eeed2ecf29977bf97c52)](https://sonarqube.cs.ui.ac.id/dashboard?id=navigo-ppl)

# Running
1. Ensure you have `.env` contains `GEMINI_API_KEY=TTEST`
2. Then load env into the uvicorn
`uvicorn app.main:app --reload --env-file .env`