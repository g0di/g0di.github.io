---
layout: post
title: Integrating Problem Details RFC with FastAPI
tags: python library api
---

During my past development projects, I built a lot of HTTP APIs using various langages (TypeScript, JavaScript, Python) and frameworks (fastify, FastAPI, flask, express). One thing I've noticed is that each of those frameworks have their own way of shaping HTTP error responses. This is actually not a big deal considering that most clients (i.e: HTTP clients) do not really rely on strict structure for such errors.

Most of the time, clients just raise some errors when an invalid HTTP status code is received and eventually implements some custom logic for extracting useful information (if any) from the actual response. Still, I always kept a bad taste in my mouth regarding this, it felt not professional nor good enough to me and I always ended up trying to create useful spec (OpenAPI spec) for my errors schema.

This had two downsides:

- I had to keep the same error structure in each of my APIs while I was always asking myself if the current schema was fine. This was pretty clunky
- It involved lot of boilerplate code to be copy pasted among all APIs to reuse the same error handling logic and structure

## Here comes "Problem Details for HTTP APIs" RFC

A couple of years ago I discovered a RFC, [Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807), trying to provide a standard for shaping HTTP error responses for HTTP APIs. I started to shape my errors following this RFC because:

- Even if its not a standard I could rely on a single source of truth, made and maintained by people probably smarter than me
- I could share that RFC to APIs clients preventing me to have to build and maintain documentation regarding my errors

## Integrating the RFC

Later on I started to work with `fastapi` for building my APIs in Python so I decided to customize my HTTP errors to match the Problem Details RFC. In the meanwhile a newest version was released, [RFC 9457](https://datatracker.ietf.org/doc/html/rfc9457) so I implemented that one instead. Also, that RFC started to get more and more attention from the community and I could found several articles talking about it and how to use it. Even the Zalando development team, in their excellent [RESTful API Guidelines](https://opensource.zalando.com/restful-api-guidelines/#176) (which is my bible for APIs development) adviced on using Problem Details for your API error response. On the swagger.io blog you can find [an article talking about that RFC](https://swagger.io/blog/problem-details-rfc9457-api-error-handling/) (pretty dense). I felt that it was a good thing for clients to shape HTTP errors in a standard way so I started to copy paste the same boilerplate code in all my APIs.

Spoiler alert, it actually requires a bit of code to actually implements that RFC properly in a FastAPI API and it felt not so great to copy paste that same boilerplate code on each of my APIs (it is not just about copy pasting a single 4 lines function). Considering the fact that Sebastian Ramirez (FastAPI creator) was probably not about integrating that RFC in FastAPI by default (Actually I'm not sure if it has been requested or not) I decided to look for an open source library doing that.

### fastapi-rfc7807

First, I ended up on the [fastapi-rfc7807](https://github.com/vapor-ware/fastapi-rfc7807) library. It looked like it was doing the job but the first thing that striked me is that the name of the repo actually match the previous obsolete version of the RFC, not a good starting point. Also, latest commit is about 3 years ago, not a good sign. Finally, the code implementation looked very complicated considering the own custom implementation I could have made for my own APIs. Next.

### fastapi-problem

Then I stumbled upon [fastapi-problem](https://github.com/NRWLDev/fastapi-problem). Name: OK, Latest commit last week: OK, implementation: Not as expected. I'm pretty sure that library would do the job but it got some limitations for my use cases.

I wanted to distinguish between a `Problem` object (A Pydantic model), a `ProblemException` and a `ProblemResponse` to allow developers to either return a `Problem` object, raise a `ProblemException` or also directly return `ProblemResponse` to follow on fastapi own implementation (You can return a `dict`, raise a `HTTPException` or returns a `JSONResponse` directly). Depending on your situation, being able to do all of those and still ends up with a Problem Details error response is very convenient. The `fastapi-problem` is just providing a single `Problem` class being actually an exception. This is limiting for example if you want to add custom error handlers.

```python
from fastapi_problem.error import Problem

class OutOfCreditError(DomainException):
    pass


@app.exception_handler(OutOfCreditError)
def handle_out_of_credit_error(_: Request, error: OutOfCreditError):
    raise Problem(...) # This will not work
    return Problem(...) # This will not work either
```

> Note that this is just for illustrating, the code is not working

> Note 2: I'm not 100% this is not possible with the library, I could have missed it will reviewing

This kind of situation happens most of the time in my case because I never mix `Problem Details` with my core (i.e: domain) exceptions. I keep them agnostic of the transport layer (HTTP here) which is going against the recommended way of the library which is to do the following:

```python
from fastapi_problem.error import UnprocessableProblem


class OutOfCreditError(UnprocessableProblem):
    title = "You have not enough money for doing that"


class BankingService:
    def withdraw(self):
        raise OutOfCreditError
```

The issue is that we are crossing boundaries between our core domain and our primary adapter (HTTP API). Problem Details is just a way of shaping HTTP error response, it has actually nothing to do with our domain errors. If my program is performing withdraw operations based on events instead of HTTP calls, that Problem Details becomes out of scope and my code is polluted with integration concerns.

Also, the library is missing a small but important thing for me, documenting errors as Problem Details in OpenAPI specification.
As far as I know, you can not document your API routes to indicates it can returns Problem Details

```python
# This is not working
@app.route("/withdraw", responses={422: {"model": OutOfCreditError}})
def withdraw():
    ...
```

To finish on a good note, it actually handles CORS headers in error response (which is not the case by default for FastAPI and the CORS middleware I think).

### fastapi-problem-details

Finally, during one of my professional project where I had to write lot of APIs, I decided to take the opportunity to write my own library, [fastapi-problem-details](https://github.com/g0di/fastapi-problem-details). It is simple and goes straight to the point for my use case. You can find lot of examples/behaviors on the documentation. It contains the following features:

- Add a `default` response to all route documented as returning a Problem Details HTTP Response
  ![FastAPI problem details default response](/assets/images/fastapi-problem-details-default-response.png)
- Add ability to raise `ProblemException` instead of `HTTPException` to returns error responses as Problem Details
- Transform all API errors automatically into Problem Details response including: unhandled errors, validation errors and (starlette) http exceptions
- Respect the original RFC (The `Problem` schema is aligned with what is recommended in the standard)
- Add ability to return a `ProblemResponse` directly. This is useful when you'll register your own error handlers
- Add ability to change validation error code (422 by default) and/or detail
- Add ability to include Python unhandled exception types and stack traces for debugging purposes (disabled by default)
- Add ability to document your route error responses with Problem Details OpenAPI Schema

I suggest you to give it a try and do not hesitate to open tickets on the github repo. I'll probably try to enhance the documentation is the next days so stay tuned.

> Note that even if I'm experienced with Python, this is my very first time publishing an open source Python library on github and Pypi, any advices are welcome
