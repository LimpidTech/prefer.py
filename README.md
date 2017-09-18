What is it? [![CircleCI](https://img.shields.io/circleci/project/github/LimpidTech/prefer.py.svg?style=flat-squared)](https://circleci.com/gh/LimpidTech/prefer.py) [![Coveralls](https://img.shields.io/coveralls/LimpidTech/prefer.py.svg?style=flat-sqared)](https://coveralls.io/github/LimpidTech/prefer.py)
-----------

Prefer is a library for helping you manage application configurations while
providing your users the flexibility of using whatever configuration format
fits their needs.

It provides a set of interfaces which provide standard methods for
reading arbitrary project configuration data. This can vary from simple cases
like JSON, to more complicated examples - such as retreiving configuration data
from a database.


How do I use it?
----------------

Firstly, you'll want to install the module. This can be done easily with
`easy_install` or `pip`.

```sh
easy_install prefer

```

Prefer is fairly simple to use. A basic use case might be that you have the
following JSON configuration in *settings.json*:

```json
{
  "auth": {
    "username": "user",
    "password": "pass"
  }
}
```

You can load these settings with the following code using promises:

```python
import prefer

configuration = await prefer.load('settings')
username = configration.get('auth.username')
```

You will notice that prefer only required 'settings' as the filename. It is
recommended to be given without a path or extension, because prefer takes care
of looking through the filesystem for configuration files. On both Unix and
Windows systems, it will look in all of the standard folders, as well as some
conventional places where people like to put their configurations.

Ordering matters, so having a file in `./settings.json` as well as another in
`/etc/settings.json` is still reliable. The configuration in `./settings.json`
will be used first. Prefer doesn't care what format your user writes your
settings in, so they can also use `settings.yaml` if they like.


Supported configuration formats
-------------------------------

Along with being fully configurable to support any arbitrary data source you'd
like, the following types of data can immediately be used as configuration formats
upon installation of prefer:

- JSON
- YAML


Why asyncronous?
----------------

In order to supply a more-simple method of getting the configuration, many
configuration tools prefer to provide a blocking method of retrieving a project
configuration. One goal of prefer is to ensure that we aren't limiting users to
specific use-cases - and some projects require real-time, dynamic updating of
their configuration. Prefer provides all it's interfaces as asyncronous
functions in order to provide that possibility without the requirement that
those actions are blocking.



[cov]: http://monokro.me/projects/prefer/coverage.html
[bs]: https://travis-ci.org/LimpidTech/prefer.png?branch=master "Build Status"
[j5]: http://json5.org/ "json5 - JSON for the ES5 era"
