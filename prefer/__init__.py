__author__ = "Bailey Stoner <monokrome@monokro.me>"
__version__ = "0.2.1"

from prefer import builder as builder_module
from prefer import loading
from prefer import watch as watch_module

load = loading.load
watch = watch_module.watch
LoadOptions = loading.LoadOptions

ConfigBuilder = builder_module.ConfigBuilder
Source = builder_module.Source
MemorySource = builder_module.MemorySource
FileSource = builder_module.FileSource
OptionalFileSource = builder_module.OptionalFileSource
EnvSource = builder_module.EnvSource
deep_merge = builder_module.deep_merge
