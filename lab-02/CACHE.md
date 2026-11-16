# Lab 02 - Cache Experiment

## Cache implementation

I enabled pip dependency caching in the GitHub Actions `test` job using `actions/setup-python@v5`.

The cache key is based on `lab-02/requirements.txt` and `lab-02/requirements-dev.txt`, so changes to dependencies invalidate the existing cache.

## Measurements

| Metric | Cold run | Warm run |
|---|---|---|
| Cache status | Miss | Hit |
| Set up Python | 1s | 2s |
| Install dependencies | 3s | 3s |
| Total test job | 12s | 12s |

The cold run reported `pip cache is not found`.

The warm run reported `Cache restored successfully` and restored approximately 7 MB.

## Conclusion

Caching was successfully configured and verified through GitHub Actions logs.

However, the measured dependency installation time remained at 3 seconds, and the overall test job took 12 seconds in both runs.

The cache did not produce a measurable speed improvement in this experiment, likely because the project has relatively few dependencies and restoring the cache introduces its own overhead.

The benefit may become more noticeable with larger dependency sets or slower package downloads.