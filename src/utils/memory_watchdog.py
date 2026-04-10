import psutil
import gc
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemoryWatchdog:
    """
    A Watchdog felel a RAM szint aktív figyeléséért.
    Ha a memóriafogyasztás eléri a kritikus szintet (alapértelmezetten 80%),
    kényszerített szemétgyűjtést (Garbage Collection) hajt végre, és vár.
    Kifejezetten hasznos 16GB RAM és AM3/Phenom II architektúra esetén.
    """
    def __init__(self, threshold_percent=80.0, sleep_time=2.0):
        self.threshold_percent = threshold_percent
        self.sleep_time = sleep_time

    def get_memory_usage(self):
        """Visszaadja a jelenlegi memóriafogyasztást százalékban."""
        mem = psutil.virtual_memory()
        return mem.percent

    def check(self):
        """
        Ellenőrzi a RAM állapotát. Ha túlléptük a küszöböt,
        megpróbál memóriát felszabadítani, és várakozik.
        """
        usage = self.get_memory_usage()

        if usage >= self.threshold_percent:
            logging.warning(f"Kritikus memóriaszint elérve: {usage}%. Kényszerített tisztítás...")

            # Memória felszabadítása
            gc.collect()

            # Újra ellenőrizzük a használatot tisztítás után
            post_gc_usage = self.get_memory_usage()
            logging.info(f"Szemétgyűjtés utáni memória: {post_gc_usage}%.")

            # Phenom II esetén hasznos lehet hagyni a CPU-t lehűlni, miközben
            # a lapozófájl (swap) rendeződik.
            logging.info(f"Várakozás {self.sleep_time} másodpercig a processzor pihentetése és az I/O rendezése céljából...")
            time.sleep(self.sleep_time)

            # Ha továbbra is kritikus, jelezzük
            if post_gc_usage >= self.threshold_percent:
                logging.error("A memóriaszint a tisztítás ellenére is kritikus!")
        else:
            logging.debug(f"Memóriaszint stabil: {usage}%.")

if __name__ == "__main__":
    # Egyszerű teszt a watchdoghoz
    watchdog = MemoryWatchdog(threshold_percent=50.0) # Alacsony küszöb teszteléshez
    watchdog.check()
