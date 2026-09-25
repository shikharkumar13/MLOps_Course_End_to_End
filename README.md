### MLOps for ML Practitioners
 
A 13-part series on taking a machine learning model from a notebook to a real, monitored, automatically-deployed system. Built around one rule: **every command, every piece of code, and every tool version in these articles was actually run before it was written down.**
 
Where a claim could go stale, it's noted honestly instead of glossed over: MLflow's storage backend recently switched defaults in a way most existing tutorials haven't caught up to, the Model Registry's classic "stages" API is deprecated in favor of aliases, and at least four real bugs (a wrong accuracy figure, a broken AIC/BIC calculation, a narrative sequencing error, a `list`-vs-`tuple` crash) were caught by actually re-running the code before publishing, not assumed correct on the first pass.
 
---
 
## What is MLOps?
 
A trained model that works on your laptop and a system real users can depend on are two different achievements. MLOps, machine learning operations, is the engineering discipline that closes that gap: the practices, tools, and habits that make a model reliable, reproducible, and observable once it leaves your notebook.
 
It rests on four pillars, and this series is organized around building each one, in order:
 
- **Versioning.** Code, data, and models tracked together, so you can always answer what exactly produced a given prediction.
- **Reproducibility.** The same code, data, and parameters produce the same model, on any machine, not just yours.
- **Automation.** Building, testing, training, and deploying happen through repeatable pipelines instead of manual, error-prone steps.
- **Monitoring.** Something is always watching how a deployed model performs against fresh, real-world data, so decay gets caught in days, not in a quarterly report.
Why it's worth taking seriously: independent estimates from VentureBeat, Gartner, and McKinsey, taken across different years and methodologies, consistently find that most ML projects never reach production, and Article 0 walks through two real, opposite outcomes: Zillow's algorithmic home-buying business, which lost over $500 million partly because nothing was watching the model for drift, and Uber's internal Michelangelo platform, which turned "get a model to production reliably" into a solved, reusable capability across hundreds of projects.
 
---
 
## The Articles
 
All 13 pieces build on one real, continuous project starting at Article 7.5: predicting customer churn on the real IBM Telco Customer Churn dataset (7,043 customers). Nothing before Article 7.5 uses invented placeholder projects either, Articles 1-7 use real datasets (Iris, UCI Heart Disease) throughout.
 
HTML files in this repo won't render in GitHub's own file viewer, GitHub only shows raw HTML as text. Enable **GitHub Pages** for this repository (Settings → Pages → deploy from branch, root) and the links below will open properly in a browser.
 
| # | Article | What it covers | Link |
|---|---------|-----------------|------|
| 0 | **Introduction to MLOps** | Why ML needs its own engineering discipline: real failure-rate statistics, the Zillow and Uber case studies, the four pillars, and the roadmap this series follows | [Article 0](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_0_Introduction_to_MLOps.html) |
| 1 | **Git & GitHub, Complete Guide** | Every core Git and GitHub concept and command, from a first commit to resolving a merge conflict | [Article 1](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_1_Git_GitHub_Complete_Guide.html) |
| 2 | **Git Hands-On: Iris Project** | The full Git workflow practiced end to end on a real classifier project | [Article 2](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_2_Git_ML_Project_Practice.html) |
| 3 | **Git + DVC: Heart Disease Project** | Versioning data and trained models alongside code, including a full pipeline and byte-for-byte time travel | [Article 3](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_3_Git_DVC_Heart_Disease_Project.html) |
| 4 | **Docker Fundamentals & Dockerfile** | Images, containers, layers, and writing a real Dockerfile line by line | [Article 4](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_4_Docker_Fundamentals_and_Dockerfile.html) |
| 5 | **Docker Hands-On: ML Project** | Containerizing a trained model and its Flask API into one portable image | [Article 5](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_5_Docker_ML_Project_Practice.html) |
| 6 | **Flask for ML Deployment** | Wrapping a trained model in a REST API, and the exact gotchas that break it in production | [Article 6](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_6_Flask_for_ML_Deployment.html) |
| 7 | **FastAPI & Pydantic for ML Deployment** | Modern, self-documenting API serving with automatic request validation | [Article 7](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_7_FastAPI_Pydantic_for_ML_Deployment.html) |
| 7.5 | **End-to-End Churn Pipeline** | The checkpoint: Git, DVC, Docker, and FastAPI wired into one real, continuous project on the Telco Customer Churn dataset | [Article 8](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_7.5_End_to_End_Churn_Pipeline.html) |
| 8 | **MLflow Experiment Tracking** | Logging every training run's parameters, metrics, and models so nothing gets lost or forgotten | [Article 8](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_8_MLflow_Experiment_Tracking.html) |
| 9 | **MLflow Model Registry** | Managing which model version is actually live, using aliases rather than the deprecated stages API | [Article 9](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_9_MLflow_Model_Registry.html) |
| 10 | **Pipeline Orchestration with Prefect** | Automating training, tracking, and promotion to run on their own, on a schedule, with retries and caching | [Article 10](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_10_Pipeline_Orchestration_with_Prefect.html) |
| 11 | **CI/CD with GitHub Actions** | Testing, building, and shipping a Docker image automatically on every pull request | [Article 11](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_11_CI_CD_with_GitHub_Actions.html) |
| 12 | **Unified Implementation** | Tying MLflow, Prefect, and GitHub Actions together into one real, networked system rather than four separate demos | [Article 12](https://shikharkumar13.github.io/MLOps_Course_End_to_End/Article_12_Unified_Implementation.html) |
 
---
 
## What makes this series different
 
Most MLOps material either stays entirely theoretical or demonstrates one tool in isolation. This series does neither:
 
- **One project, the whole way through.** Starting at Article 7.5, the same churn model is trained, tracked, registered, orchestrated, tested, and deployed, with every article's numbers matching exactly, because it's the same code and data every time.
- **Nothing is asserted without running it.** Server startup times, exact error messages, deprecation warnings, and API responses quoted in these articles come from actually executing the code, not from memory or documentation alone.
- **Version drift is called out, not hidden.** MLflow's default tracking backend changed to SQLite in a recent release, something most existing tutorials still don't reflect, and the Model Registry's stage-based API is explicitly flagged as deprecated with the current alias-based replacement taught instead.
- **Mistakes found during verification are shown, not silently fixed.** Several articles include a real bug that was caught by re-running the published code, what it was, and how it was corrected, rather than presenting a first draft as if it were always correct.
---
 
## Repository layout
 
```
.
├── Article_0_Introduction_to_MLOps.html         ... through ...
├── Article_12_Unified_Implementation.html
└── README.md
```
 
## License
 
MIT.
