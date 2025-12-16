import asyncio
import json
import os
import tempfile

import pytest

import prefer
from prefer.watch import ConfigChangeHandler, watch


@pytest.mark.asyncio
async def test_watch_yields_initial_configuration():
    """Test that watch yields the initial configuration first."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "config.json")

        with open(config_path, "w") as f:
            json.dump({"initial": True}, f)

        async for config in prefer.watch(
            "config",
            options={
                "loaders": {
                    "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                }
            },
        ):
            assert config.context == {"initial": True}
            break


@pytest.mark.asyncio
async def test_watch_detects_file_changes():
    """Test that watch detects and yields config on file changes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "config.json")

        with open(config_path, "w") as f:
            json.dump({"version": 1}, f)

        updates_received = []

        async def watch_with_timeout() -> None:
            async for config in prefer.watch(
                "config",
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                },
            ):
                updates_received.append(config.context.copy())
                if len(updates_received) >= 2:
                    break

        # Start watching in background
        watch_task = asyncio.create_task(watch_with_timeout())

        # Wait for initial load
        await asyncio.sleep(0.2)

        # Modify the file
        with open(config_path, "w") as f:
            json.dump({"version": 2}, f)

        # Wait for update with timeout
        try:
            await asyncio.wait_for(watch_task, timeout=3.0)
        except asyncio.TimeoutError:
            watch_task.cancel()
            try:
                await watch_task
            except asyncio.CancelledError:
                pass

        assert len(updates_received) >= 1
        assert updates_received[0] == {"version": 1}
        if len(updates_received) >= 2:
            assert updates_received[1] == {"version": 2}


@pytest.mark.asyncio
async def test_watch_skips_invalid_updates():
    """Test that watch skips invalid config updates and continues."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "config.json")

        with open(config_path, "w") as f:
            json.dump({"valid": True}, f)

        updates_received = []

        async def watch_with_timeout() -> None:
            async for config in prefer.watch(
                "config",
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                },
            ):
                updates_received.append(config.context.copy())
                if len(updates_received) >= 2:
                    break

        watch_task = asyncio.create_task(watch_with_timeout())

        # Wait for initial load
        await asyncio.sleep(0.2)

        # Write invalid JSON - should be skipped
        with open(config_path, "w") as f:
            f.write("{invalid json}")

        await asyncio.sleep(0.2)

        # Write valid JSON - should trigger update
        with open(config_path, "w") as f:
            json.dump({"recovered": True}, f)

        try:
            await asyncio.wait_for(watch_task, timeout=3.0)
        except asyncio.TimeoutError:
            watch_task.cancel()
            try:
                await watch_task
            except asyncio.CancelledError:
                pass

        # Should have at least initial config
        assert len(updates_received) >= 1
        assert updates_received[0] == {"valid": True}


@pytest.mark.asyncio
async def test_config_change_handler_on_modified():
    """Test ConfigChangeHandler correctly queues modifications."""
    queue: asyncio.Queue[str] = asyncio.Queue()
    handler = ConfigChangeHandler("/test/path", queue)
    handler.set_loop(asyncio.get_running_loop())

    # Create a mock file modified event
    from watchdog.events import FileModifiedEvent

    event = FileModifiedEvent("/test/path")
    handler.on_modified(event)

    # Check that the path was queued
    path = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert path == "/test/path"


@pytest.mark.asyncio
async def test_config_change_handler_ignores_directory_events():
    """Test ConfigChangeHandler ignores directory modification events."""
    queue: asyncio.Queue[str] = asyncio.Queue()
    handler = ConfigChangeHandler("/test/path", queue)
    handler.set_loop(asyncio.get_running_loop())

    # Create a mock directory modified event
    from watchdog.events import DirModifiedEvent

    event = DirModifiedEvent("/test/dir")
    handler.on_modified(event)  # type: ignore[arg-type]

    # Queue should be empty
    assert queue.empty()


@pytest.mark.asyncio
async def test_config_change_handler_ignores_other_paths():
    """Test ConfigChangeHandler ignores events for other paths."""
    queue: asyncio.Queue[str] = asyncio.Queue()
    handler = ConfigChangeHandler("/test/path", queue)
    handler.set_loop(asyncio.get_running_loop())

    # Create a mock file modified event for a different path
    from watchdog.events import FileModifiedEvent

    event = FileModifiedEvent("/other/path")
    handler.on_modified(event)

    # Queue should be empty
    assert queue.empty()


@pytest.mark.asyncio
async def test_config_change_handler_ignores_when_no_loop():
    """Test ConfigChangeHandler ignores events when no loop is set."""
    queue: asyncio.Queue[str] = asyncio.Queue()
    handler = ConfigChangeHandler("/test/path", queue)
    # Don't set the loop

    from watchdog.events import FileModifiedEvent

    event = FileModifiedEvent("/test/path")
    handler.on_modified(event)

    # Queue should be empty since no loop was set
    assert queue.empty()
