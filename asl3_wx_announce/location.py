from typing import Tuple, Dict, Optional
import json
import logging
import socket

class LocationService:
    # Class-level cache to persist across multiple instantiations if needed
    # though usually this service is re-instantiated. If that's the case, we might need a file-based or global cache.
    # For now, let's assume `main.py` instantiates it once or we make this class attribute.
    _last_known_gps: Optional[Tuple[float, float]] = None

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_coordinates(self) -> Tuple[float, float]:
        """
        Returns (lat, lon).
        Checks 'type' config: 'fixed' (default) or 'auto' (GPS via gpsd).
        If GPS fails, falls back to the last known GPS fix, then to fixed config.
        """
        if self.config.get('location', {}).get('type') == 'auto':
            try:
                lat, lon = self._read_gpsd()
                # Update cache on success
                LocationService._last_known_gps = (lat, lon)
                return lat, lon
            except Exception as e:
                self.logger.warning(f"GPS read failed: {e}")

                # Fallback 1: Last Known GPS
                if LocationService._last_known_gps:
                    self.logger.info(f"Using last known GPS coordinates: {LocationService._last_known_gps}")
                    return LocationService._last_known_gps

                # Fallback 2: Fixed Config
                self.logger.warning("No last known GPS. Falling back to fixed/static.")

        # Static fallback
        lat = self.config.get('location', {}).get('latitude')
        lon = self.config.get('location', {}).get('longitude')
        if lat is None or lon is None:
            raise ValueError("No valid location coordinates found in config or GPS.")
        return float(lat), float(lon)

    def _read_gpsd(self) -> Tuple[float, float]:
        # Simple socket reader for GPSD standard port 2947
        # We start the WATCH command and wait for a TPV report
        try:
            with socket.create_connection(('localhost', 2947), timeout=2) as sock:
                sock.sendall(b'?WATCH={"enable":true,"json":true}\n')
                fp = sock.makefile()
                for line in fp:
                    data = json.loads(line)
                    if data.get('class') == 'TPV':
                        lat = data.get('lat')
                        lon = data.get('lon')
                        if lat and lon:
                            return lat, lon
        except Exception as e:
            raise e
        raise RuntimeError("No TPV data received from GPSD")
