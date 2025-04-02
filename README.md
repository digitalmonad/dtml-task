# GitHub Events Monitor

GitHub Events Monitor is a FastAPI-based application that monitors particular public events from the GitHub API and provides metrics via a REST API.

**The app is part of a interview task, which original assignment was:**


_For that we want you to stream specific events from the Github API (https://api.github.com/events)._

_The events we are interested in are the WatchEvent, PullRequestEvent and IssuesEvent. Based on the collected events, metrics shall be provided at any time via a REST API to the end user._

_The following metrics should be implemented:_
- _Calculate the average time between pull requests for a given repository._
- _Return the total number of events grouped by the event type for a given offset. The offset determines how much time we want to look back i.e., an offset of 10 means we count only the events which have been created in the last 10 minutes._

_Bonus assignment - Add another REST API endpoint providing a meaningful visualization of one of existing metrics or a newly introduced metric._

_Please add a README file to your solution that contains how to run the solution and a brief description about your assumptions. To get an idea of your documentation skills, we ask you to create a simple diagram of your application preferably regarding the C4 (level 1) model rules (https://c4model.com/)._

_The assignment will have to be made in Python._

_We expect it will take 8 hours to do it properly._

**From this a formulated following requirements:**

### Functional requirements:
- [ ] Fetch GitHub events from https://api.github.com/events.

- [ ] Filter and process only the following event types: 
    - WatchEvent
    - PullRequestEvent
    - IssuesEvent

- [ ] The app should provide REST API Endpoints that:
   - [ ] Calculate the average time between pull requests (particularly PullRequestEvent) for a given repository.
   ```GET /metrics/events/pull_request/average/{repository_name}```
   - [ ] Return the total number of events grouped by type (all event types) for a given time offset (in minutes).
   ```GET /metrics/events/{event_type}/total?offset={minutes}```
   - [ ] (Optional) Provide a meaningful visual representation of an existing (all event types) or newly introduced metric.
   ```GET /visualization/{metric_name}```

- [ ] Store collected events in a persistent or semi-persistent data store (e.g., database or in-memory storage)
Since we want to compute the metrics based on arbitrary date offset in minutes, we need to store them for reasonable amount of time.

### Non-Functional Requirements

- [X] Provide project documentation in form of a README file
- [ ] Write reasonable amount of testing code


## Solution

### 1) Rate limiting

GitHub provides both public (unauthenticated) and personal (authenticated) limits for their API.

Primary limiting factor is count of calls per hour.
- public limit is 60 calls per hour
- personal is 5000 calls per hour

Secondary limits are not relevant for our use case, since I don't see them restricting at this moment.

-> [Rate limit docs](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)

I presume that this app shall use the unauthenticated API as its part of the challenge to figure out how to work with the rate limiting. Also the user of the app would be forced to generate his access token.

As the 

### 2) Metrics scraping

The https://api.github.com/events endpoint gives back an array of last 10 endpoints
Github also provides [endpoint](https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-repository-events) for fetching just the events happening at particular repo.
Since the assignment explicitly states that "Based on the collected events, metrics shall be provided...", I will ignore this endpoint and I'll work just with the ```/events``` endpoint to get the data.

The docs explicitly says that the GitHub keeps just last 300 latest events and is paginated and the offset can be set (default is 10, maximum 100). Since we aim to make as little as possible API calls it makes sense to make 3 calls with offset 100. Each event has a unique ID, so we can detect potential duplicities easily.

Given that public GitHub REST API provides only 60 requests (otherwise access is denied) it makes sense to scrape data 20 times per minute at maximum (60/3=20).


