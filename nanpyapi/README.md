NanpyAPI
========

Simple RESTful Web API to control Arduino pins with Nanpy & Flask

Dependencies
------------

- nanpy > 0.5
- flask

Some examples using curl
------------------------

Read from analog pin 0

	curl http://127.0.0.1:5000/arduino/analogpin/0

Write 1 on digital pin 13

	curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/arduino/digitalpin/13 -d '{"value":1}'


