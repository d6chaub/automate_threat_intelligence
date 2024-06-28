# High-Level
- Make an API to update configs dynamically? Make another one to get the configs as well... where should I provide the configs..
- Make the configs pull from the db... make it a collection in the db... and then at pipeline startup make it pull from the db..
- For the configs think I should make a backend that calls all the API things...
- Find the best way to integration test the fetching (from feedly) and the storing into the database (mongo).
- Read up more on pytest fixtures, how many times they're run on a class / when applied to separate functions, etc.
- Install 
- Think about testing in docker image... make a test docker environment that installs pytest and runs the tests? Make it a multi-stage build, and the prod environment doesn't have that..
- Consider whether to use the .get_dao method at all, or just hard-code the MongoClient. Might be simpler. Think about it. For now I'm only using the .get_dao method in the tests.



- For local dev set up the environment right so the parser works properly.
- use something like mypy and configure with ci/cd and pre-commits to make static type-checking better...


# Next:

- Sort out the bicep files with Mike... find the 'existing' ones...