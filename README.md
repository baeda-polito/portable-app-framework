# Anomaly detection and diagnosis framework

## Table of contents

* [Test](#test)

### Test

Tests are implemented in the test folder. The tests are run using the `pytest` library and an automatic testing is
enabled by the github action `pytest.yml` file.

### Automations

* Deploy `docs` to the branch `gh-pages` through Github action. The action is triggered when a push is made to the
  branch `main`. The action is defined in the
  file [`.github/workflows/deploy_docs.yml`](./.github/workflows/deploy_docs.yml) and is adapted
  from [this](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
  The rendered website is available
  at [https://robertochiosa.github.io/afdd-polito-berkeley/intro.html](https://robertochiosa.github.io/afdd-polito-berkeley/intro.html)
* Automatic testing are performed though a github action using
  pytest [`.github/workflows/pytest.yml`](./.github/workflows/pytest.yml) at each push of the branch `main`.

## Contribution

Feel free to contribute any kind of function or enhancement, here the coding style follows PEP8

Code should pass the [Flake8](http://flake8.pycqa.org/en/latest/) check before committing.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for more details

## Acknowledgements

* This project structure is inspired by the
  GitHub project [Tensorflow-Project-Template](https://github.com/MrGemy95/Tensorflow-Project-Template)
  by [Mahmoud Gemy](https://github.com/MrGemy95)