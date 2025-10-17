# Contributing to Predictive Reliability Platform

Thank you for your interest in contributing to this project!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/suhasramanand/predictive-reliability-platform.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test locally: `make up && make test`
6. Commit your changes: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guide
- **TypeScript**: Use ESLint and Prettier configurations
- **Docker**: Keep Dockerfiles minimal and layered efficiently
- **YAML**: Use 2-space indentation

### Testing

- Test all changes locally with Docker Compose
- Ensure health checks pass: `make health`
- Run chaos tests to verify resilience: `make chaos`
- Check logs for errors: `make logs`

### Documentation

- Update README.md if adding new features
- Add comments to complex code sections
- Update API documentation (FastAPI auto-generates)
- Include examples for new functionality

## Areas for Contribution

### Enhancement Ideas

- **Anomaly Detection**: Implement advanced ML models (LSTM, Prophet, ARIMA)
- **Policy Engine**: Add more action types (scale down, circuit breaker, rate limiting)
- **Dashboard**: Additional visualizations, real-time charts, custom dashboards
- **Integrations**: Slack alerts, PagerDuty, email notifications, webhooks
- **Microservices**: Add more example services, different tech stacks
- **Chaos Engineering**: More sophisticated failure scenarios
- **Kubernetes**: Add K8s manifests, Helm charts
- **Terraform**: Add modules for AWS, GCP, Azure

### Bug Reports

If you find a bug:
1. Check existing issues first
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Docker version)
   - Logs if applicable

### Feature Requests

1. Open an issue describing the feature
2. Explain the use case and benefits
3. Discuss implementation approach
4. Wait for feedback before implementing

## Pull Request Process

1. **Update documentation** for any new features
2. **Add tests** if applicable
3. **Keep commits atomic** - one logical change per commit
4. **Write clear commit messages**
5. **Link to related issues** in PR description
6. **Respond to code review** feedback promptly

## Code Review Criteria

Pull requests will be evaluated on:
- Code quality and clarity
- Test coverage
- Documentation completeness
- Adherence to existing patterns
- Performance impact
- Security considerations

## Questions?

Open an issue for questions or reach out via GitHub Discussions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

