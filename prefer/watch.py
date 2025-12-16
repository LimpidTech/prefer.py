"""File watching functionality for configuration files."""

from __future__ import annotations

import asyncio
import typing

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from prefer import configuration as configuration_module
from prefer import loading

if typing.TYPE_CHECKING:
    from collections.abc import AsyncIterator


class ConfigChangeHandler(FileSystemEventHandler):
    """Handler for file system events that queues config updates."""

    def __init__(self, path: str, queue: asyncio.Queue[str]) -> None:
        super().__init__()
        self.path = path
        self.queue = queue
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop to use for queue operations."""
        self._loop = loop

    def on_modified(self, event: FileModifiedEvent) -> None:  # type: ignore[override]
        """Handle file modification events."""
        if event.is_directory:
            return

        if event.src_path == self.path and self._loop is not None:
            self._loop.call_soon_threadsafe(self.queue.put_nowait, self.path)


async def watch(
    identifier: str,
    *,
    options: loading.LoadOptions | None = None,
) -> AsyncIterator[configuration_module.Configuration]:
    """Watch a configuration file for changes.

    Yields Configuration objects whenever the file is modified.
    The first yield is the initial configuration load.

    Args:
        identifier: The configuration file identifier to watch.
        options: Optional loading options.

    Yields:
        Configuration objects on initial load and each file modification.

    Example:
        async for config in watch("settings"):
            print(f"Config updated: {config.get('key')}")
    """
    # Initial load to get the actual file path
    config = await loading.load(identifier, options=options)
    yield config

    # Get the actual file path from the loader result
    if config.loader is None:  # pragma: no cover
        return

    paths = await config.loader.locate(identifier)
    if not paths:  # pragma: no cover
        return

    file_path = paths[0]

    # Set up file watching
    queue: asyncio.Queue[str] = asyncio.Queue()
    handler = ConfigChangeHandler(file_path, queue)
    handler.set_loop(asyncio.get_running_loop())

    observer = Observer()
    # Watch the directory containing the file
    import os

    watch_dir = os.path.dirname(file_path) or "."
    observer.schedule(handler, watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            # Wait for file change notification
            await queue.get()

            # Small delay to let file writes complete
            await asyncio.sleep(0.05)

            # Reload configuration, skip errors (resilient watching)
            try:
                config = await loading.load(identifier, options=options)
                yield config
            except Exception:
                # Skip invalid configs, continue watching
                continue
    finally:
        observer.stop()
        observer.join(timeout=1.0)
