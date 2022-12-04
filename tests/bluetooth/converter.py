from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

from pokecon_extensions.bluetooth import Config, from_virtual_serial

if __name__ == "__main__":

    config = Config(port="COM6", baudrate=4800)

    with mp.Manager() as manager, ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(from_virtual_serial, config,
                        manager.Event(), manager.Event())
