# ⚙️ T4 — Infrastructure & Reproducibility

## Focus
CI/CD, automated testing, package publishing, and research infrastructure.

## CI/CD Pipelines
- **Test workflows** — auto-test on push for bioscore, set-method, studyreg
- **Publish workflows** — auto-publish to PyPI on tag (bioscore-v*, set-method-v*, studyreg-v*)

## Hub Infrastructure
| Hub | URL | Purpose |
|---|---|---|
| K-RnD Lab | [k-rnd-lab.vercel.app](https://k-rnd-lab.vercel.app) | Research overview |
| K Venture Studio | [k-venture-studio.vercel.app](https://k-venture-studio.vercel.app) | Venture building |
| K Mentorship Hub | [k-mentorship-hub-frontier.vercel.app](https://k-mentorship-hub-frontier.vercel.app) | Learning paths |

## Starter Tasks
1. Tag a release: `git tag bioscore-v0.3.0 && git push --tags`
2. Add tests for a new bioscore check
3. Set up Vercel analytics for your hub
4. Configure a custom domain

## Key Repos
- [SPHERE-III-TECHNOLOGY](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY)
