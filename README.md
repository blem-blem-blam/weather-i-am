To run the environment,
`poetry install`
`eval "$(poetry env activate)"`

debugging the test env
`docker compose -f docker-compose.test.yml up --wait`
`docker compose -f docker-compose.test.yml down`

Speed run tests
`./run_tests.sh `

to add libraries to dev
`poetry add pytest-cov --group dev`
